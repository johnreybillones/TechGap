"""
Inspect the actual HTML returned by Bright Data for a JobStreet page.
Saves HTML to fixtures and searches for data sources.
"""

import asyncio
import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.config import ScraperConfig
from scraper.client.scraper import HybridScraperClient

FIXTURES_DIR = Path(__file__).parent / "tests" / "fixtures"


async def main():
    env_path = Path(__file__).parent.parent / ".env"
    config = ScraperConfig(_env_file=str(env_path))
    client = HybridScraperClient(config)

    url = "https://www.jobstreet.com.ph/software-developer-jobs"
    print(f"Fetching: {url}")
    html = await client.fetch_html(url, retries=2)
    print(f"Got {len(html):,} chars")

    # Save full HTML
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    (FIXTURES_DIR / "search_page_raw.html").write_text(html, encoding="utf-8")
    print(f"Saved to {FIXTURES_DIR / 'search_page_raw.html'}")

    soup = BeautifulSoup(html, "html.parser")

    # Check for __NEXT_DATA__
    next_data_tag = soup.find("script", id="__NEXT_DATA__")
    print(f"\n__NEXT_DATA__ tag found: {next_data_tag is not None}")

    # Check ALL script tags for embedded JSON data
    print("\n--- All <script> tags ---")
    scripts = soup.find_all("script")
    print(f"Total script tags: {len(scripts)}")
    for i, s in enumerate(scripts):
        tag_id = s.get("id", "")
        tag_type = s.get("type", "")
        src = s.get("src", "")
        content_len = len(s.string) if s.string else 0
        
        desc = f"[{i}] id='{tag_id}' type='{tag_type}'"
        if src:
            desc += f" src='{src[:80]}...'" if len(src) > 80 else f" src='{src}'"
        if content_len > 0:
            desc += f" content={content_len:,} chars"
            # Check if it contains job data
            text = s.string
            if "software" in text.lower() or "developer" in text.lower() or "jobTitle" in text.lower():
                desc += " ⭐ HAS JOB DATA"
        print(f"  {desc}")

    # Search for JSON-LD structured data
    json_ld = soup.find_all("script", type="application/ld+json")
    print(f"\n--- JSON-LD blocks: {len(json_ld)} ---")
    for i, tag in enumerate(json_ld):
        if tag.string:
            try:
                data = json.loads(tag.string)
                (FIXTURES_DIR / f"jsonld_{i}.json").write_text(
                    json.dumps(data, indent=2), encoding="utf-8"
                )
                print(f"  [{i}] Saved. Type: {data.get('@type', 'unknown')}, keys: {list(data.keys())[:8]}")
            except json.JSONDecodeError:
                print(f"  [{i}] Invalid JSON")

    # Search for any inline JSON that looks like job data
    print("\n--- Searching for embedded job data patterns ---")
    patterns = ["window.__NEXT_DATA__", "window.__data__", "self.__next_f", 
                "jobSearchResult", "searchResults", "jobCardViewModel",
                '"jobs":', '"data":{"search"']
    for pat in patterns:
        if pat in html:
            idx = html.index(pat)
            print(f"  ✅ Found '{pat}' at position {idx}")
            # Show context
            snippet = html[max(0, idx-20):idx+120]
            print(f"     Context: ...{snippet}...")
        else:
            print(f"  ❌ '{pat}' not found")

    # Also try a job detail page
    print("\n" + "="*50)
    print("Fetching a job detail page...")
    detail_url = "https://www.jobstreet.com.ph/job/79414730"
    try:
        detail_html = await client.fetch_html(detail_url, retries=2)
        print(f"Got {len(detail_html):,} chars")
        (FIXTURES_DIR / "detail_page_raw.html").write_text(detail_html, encoding="utf-8")

        detail_soup = BeautifulSoup(detail_html, "html.parser")
        detail_nd = detail_soup.find("script", id="__NEXT_DATA__")
        print(f"__NEXT_DATA__ in detail page: {detail_nd is not None}")

        # Check for self.__next_f pattern (RSC streaming)
        if "self.__next_f" in detail_html:
            print("  ✅ Found self.__next_f (React Server Components streaming)")
        
        # Check for JSON-LD in detail
        detail_ld = detail_soup.find_all("script", type="application/ld+json")
        for i, tag in enumerate(detail_ld):
            if tag.string:
                try:
                    data = json.loads(tag.string)
                    (FIXTURES_DIR / f"detail_jsonld_{i}.json").write_text(
                        json.dumps(data, indent=2), encoding="utf-8"
                    )
                    print(f"  JSON-LD [{i}]: @type={data.get('@type')}, keys={list(data.keys())[:10]}")
                except:
                    pass
    except Exception as e:
        print(f"  ❌ Detail fetch failed: {e}")

    print(f"\n📊 Total API requests: {client.request_count}")


if __name__ == "__main__":
    asyncio.run(main())
