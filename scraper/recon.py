"""
TechGap Scraper — Phase 1 Reconnaissance Script

This script:
1. Fetches a sample JobStreet search page via Bright Data
2. Fetches a sample job detail page via Bright Data
3. Extracts and validates the __NEXT_DATA__ JSON structure
4. Confirms all required field paths exist
5. Saves raw HTML fixtures for offline testing

Run from project root:
    python -m scraper.recon
"""

import asyncio
import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.config import ScraperConfig
from scraper.client.scraper import HybridScraperClient


# --- Sample URLs for Reconnaissance ---
SAMPLE_SEARCH_URL = "https://www.jobstreet.com.ph/software-developer-jobs"
SAMPLE_DETAIL_URL = None  # Will be extracted from search results

FIXTURES_DIR = Path(__file__).parent / "tests" / "fixtures"


def extract_next_data(html: str) -> dict | None:
    """Extract __NEXT_DATA__ JSON from raw HTML."""
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag or not script_tag.string:
        return None
    return json.loads(script_tag.string)


def find_job_urls_from_search(html: str) -> list[str]:
    """Extract job detail URLs from a search results page."""
    soup = BeautifulSoup(html, "html.parser")
    links = []

    # Method 1: Look for job card links with data-automation
    for a_tag in soup.find_all("a", attrs={"data-automation": "jobTitle"}):
        href = a_tag.get("href", "")
        if href and "/job/" in href:
            if href.startswith("/"):
                href = f"https://www.jobstreet.com.ph{href}"
            links.append(href)

    # Method 2: Fallback — look in __NEXT_DATA__ for job listings
    if not links:
        next_data = extract_next_data(html)
        if next_data:
            # Search for job arrays in the JSON
            jobs = _find_jobs_in_json(next_data)
            for job in jobs[:5]:  # Take first 5
                job_id = job.get("id", "")
                if job_id:
                    links.append(f"https://www.jobstreet.com.ph/job/{job_id}")

    return links


def _find_jobs_in_json(data, depth=0, max_depth=8) -> list[dict]:
    """Recursively search for job listing arrays in __NEXT_DATA__."""
    if depth > max_depth:
        return []
    if isinstance(data, dict):
        # Check if this looks like a job
        if "title" in data and ("id" in data or "jobId" in data):
            return [data]
        results = []
        for value in data.values():
            results.extend(_find_jobs_in_json(value, depth + 1, max_depth))
        return results
    elif isinstance(data, list):
        results = []
        for item in data:
            results.extend(_find_jobs_in_json(item, depth + 1, max_depth))
        return results
    return []


def validate_job_detail(next_data: dict) -> dict:
    """
    Validate __NEXT_DATA__ contains all required PRD fields.
    Returns a report dict.
    """
    # Try known paths to find job detail
    known_paths = [
        ["props", "pageProps", "jobDetail"],
        ["props", "pageProps", "job"],
        ["props", "pageProps", "data", "jobDetail"],
        ["props", "pageProps", "initialData", "jobDetail"],
    ]

    job = None
    found_path = None

    for path in known_paths:
        current = next_data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                current = None
                break
        if current and isinstance(current, dict) and "title" in current:
            job = current
            found_path = ".".join(path)
            break

    # Fallback: deep search
    if not job:
        jobs = _find_jobs_in_json(next_data)
        if jobs:
            job = jobs[0]
            found_path = "DEEP SEARCH (path not in known_paths)"

    if not job:
        return {"success": False, "error": "Could not find job detail in __NEXT_DATA__"}

    # Map PRD fields to expected keys
    prd_field_checks = {
        "Job Title": _check_field(job, ["title"]),
        "Job Description": _check_field(job, ["description", "content", "jobDescription"]),
        "Contract Type (workType)": _check_field(job, ["workType", "employmentType", "workTypes"]),
        "Location": _check_field(job, ["location", "jobLocation"]),
        "Salary": _check_field(job, ["salary", "compensation"]),
        "Company": _check_field(job, ["company", "advertiser", "companyName"]),
        "Posted Date": _check_field(job, ["postedAt", "createdAt", "listingDate", "postedDate"]),
        "Job ID": _check_field(job, ["id", "jobId"]),
        "Classification": _check_field(job, ["classifications", "classification", "category"]),
    }

    return {
        "success": True,
        "found_path": found_path,
        "fields": prd_field_checks,
        "sample_title": job.get("title", "N/A"),
        "all_top_level_keys": list(job.keys())[:30],
    }


def _check_field(job: dict, possible_keys: list[str]) -> dict:
    """Check if any of the possible keys exist in the job dict."""
    for key in possible_keys:
        if key in job:
            value = job[key]
            # Summarize the value type and preview
            if isinstance(value, str):
                preview = value[:100] + "..." if len(value) > 100 else value
            elif isinstance(value, dict):
                preview = f"{{dict with keys: {list(value.keys())[:5]}}}"
            elif isinstance(value, list):
                preview = f"[list with {len(value)} items]"
            else:
                preview = str(value)[:100]
            return {"found": True, "key": key, "type": type(value).__name__, "preview": preview}
    return {"found": False, "tried_keys": possible_keys}


async def main():
    print("=" * 60)
    print("  TechGap — Phase 1 Reconnaissance")
    print("=" * 60)
    print()

    # Load config
    config = ScraperConfig(_env_file=str(Path(__file__).parent.parent / ".env"))
    client = HybridScraperClient(config)

    print(f"✅ Config loaded — Provider: {config.ACTIVE_PROVIDER}")
    print()

    # --- Step 1: Fetch Search Page ---
    print(f"📄 Step 1: Fetching search page...")
    print(f"   URL: {SAMPLE_SEARCH_URL}")
    try:
        search_html = await client.fetch_html(SAMPLE_SEARCH_URL)
        print(f"   ✅ Got {len(search_html):,} characters of HTML")

        # Save fixture
        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
        fixture_path = FIXTURES_DIR / "search_page_sample.html"
        fixture_path.write_text(search_html, encoding="utf-8")
        print(f"   💾 Saved to {fixture_path}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return

    # Extract __NEXT_DATA__ from search page
    search_next_data = extract_next_data(search_html)
    if search_next_data:
        print(f"   ✅ __NEXT_DATA__ found! Top-level keys: {list(search_next_data.keys())}")
        search_nd_path = FIXTURES_DIR / "search_page_next_data.json"
        search_nd_path.write_text(json.dumps(search_next_data, indent=2, default=str), encoding="utf-8")
        print(f"   💾 Saved __NEXT_DATA__ to {search_nd_path}")
    else:
        print("   ⚠️  No __NEXT_DATA__ found in search page — may use SSR differently")

    # Extract job URLs
    job_urls = find_job_urls_from_search(search_html)
    print(f"   📋 Found {len(job_urls)} job URLs in search results")
    for i, url in enumerate(job_urls[:5]):
        print(f"      [{i+1}] {url}")

    print()

    # --- Step 2: Fetch Job Detail Page ---
    if not job_urls:
        print("   ❌ No job URLs found — cannot test detail page extraction")
        return

    detail_url = job_urls[0]
    print(f"📄 Step 2: Fetching job detail page...")
    print(f"   URL: {detail_url}")
    try:
        detail_html = await client.fetch_html(detail_url)
        print(f"   ✅ Got {len(detail_html):,} characters of HTML")

        fixture_path = FIXTURES_DIR / "detail_page_sample.html"
        fixture_path.write_text(detail_html, encoding="utf-8")
        print(f"   💾 Saved to {fixture_path}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return

    # Extract __NEXT_DATA__ from detail page
    detail_next_data = extract_next_data(detail_html)
    if not detail_next_data:
        print("   ❌ No __NEXT_DATA__ found in detail page — critical failure!")
        return

    print(f"   ✅ __NEXT_DATA__ found!")
    detail_nd_path = FIXTURES_DIR / "detail_page_next_data.json"
    detail_nd_path.write_text(json.dumps(detail_next_data, indent=2, default=str), encoding="utf-8")
    print(f"   💾 Saved __NEXT_DATA__ to {detail_nd_path}")

    print()

    # --- Step 3: Validate Field Mappings ---
    print("🔍 Step 3: Validating PRD field mappings...")
    report = validate_job_detail(detail_next_data)

    if not report["success"]:
        print(f"   ❌ {report['error']}")
        return

    print(f"   📍 Job data found at path: {report['found_path']}")
    print(f"   📌 Sample title: \"{report['sample_title']}\"")
    print(f"   🔑 Top-level keys: {report['all_top_level_keys']}")
    print()

    all_found = True
    for field_name, check in report["fields"].items():
        if check["found"]:
            print(f"   ✅ {field_name}")
            print(f"      Key: '{check['key']}' | Type: {check['type']}")
            print(f"      Preview: {check['preview'][:80]}")
        else:
            all_found = False
            print(f"   ❌ {field_name}")
            print(f"      Tried keys: {check['tried_keys']}")

    print()
    print("=" * 60)
    if all_found:
        print("  ✅ RECONNAISSANCE COMPLETE — All PRD fields confirmed!")
        print("  Next: Build extraction pipeline (Phase 3)")
    else:
        print("  ⚠️  SOME FIELDS MISSING — Review the __NEXT_DATA__ JSON")
        print(f"  Check: {detail_nd_path}")
    print("=" * 60)
    print(f"\n  Total API requests: {client.request_count}")
    print(f"  Provider: {config.ACTIVE_PROVIDER}")


if __name__ == "__main__":
    asyncio.run(main())
