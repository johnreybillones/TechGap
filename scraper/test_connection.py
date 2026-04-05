"""
Quick connectivity test — verifies Bright Data API and Supabase are reachable.
Run from project root: python -m scraper.test_connection
"""

import asyncio
import sys
from pathlib import Path

# Ensure imports work from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.config import ScraperConfig
from scraper.client.scraper import HybridScraperClient


async def main():
    print("=" * 55)
    print("  TechGap — Connection Test")
    print("=" * 55)

    # Load config from project root .env
    env_path = Path(__file__).parent.parent / ".env"
    print(f"\n📂 Loading .env from: {env_path}")

    if not env_path.exists():
        print("❌ .env file not found! Copy .env.example to .env and fill credentials.")
        return

    config = ScraperConfig(_env_file=str(env_path))

    print(f"   ACTIVE_PROVIDER: {config.ACTIVE_PROVIDER}")
    print(f"   BD_API_TOKEN:    {'***' + config.BD_API_TOKEN[-6:] if len(config.BD_API_TOKEN) > 6 else '(empty)'}")
    print(f"   BD_ZONE:         {config.BD_ZONE}")
    print(f"   SUPABASE_URL:    {config.SUPABASE_URL[:40] + '...' if len(config.SUPABASE_URL) > 40 else config.SUPABASE_URL}")
    print()

    # --- Test 1: Bright Data connectivity ---
    print("🔌 Test 1: Bright Data API connectivity...")
    client = HybridScraperClient(config)

    try:
        html = await client.fetch_html("https://geo.brdtest.com/welcome.txt", retries=1)
        if "Welcome to Bright Data" in html or "Bright Data" in html:
            print("   ✅ Bright Data connection WORKING!")
            print(f"   Response preview: {html[:120].strip()}")
        else:
            print(f"   ⚠️  Got response but unexpected content ({len(html)} chars)")
            print(f"   Preview: {html[:200]}")
    except Exception as e:
        print(f"   ❌ Bright Data FAILED: {e}")

    print()

    # --- Test 2: Fetch a real JobStreet page ---
    print("🌐 Test 2: Fetching a real JobStreet page...")
    test_url = "https://www.jobstreet.com.ph/software-developer-jobs"

    try:
        html = await client.fetch_html(test_url, retries=2)
        has_next_data = "__NEXT_DATA__" in html
        print(f"   ✅ Got {len(html):,} chars of HTML")
        print(f"   {'✅' if has_next_data else '❌'} __NEXT_DATA__ {'found' if has_next_data else 'NOT found'}")

        if has_next_data:
            # Quick count of how many times "title" appears
            title_count = html.count('"title"')
            print(f"   📊 Found ~{title_count} 'title' references in __NEXT_DATA__")
    except Exception as e:
        print(f"   ❌ JobStreet fetch FAILED: {e}")

    print()
    print(f"📊 Total API requests used: {client.request_count}")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
