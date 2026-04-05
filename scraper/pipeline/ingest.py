"""
TechGap — Apify → Supabase ETL Ingestion Pipeline
====================================================
Orchestrates the full data collection flow:
  1. Run the Apify JobStreet actor for a curated keyword list
  2. Map the results to the jobs_raw schema
  3. Upsert into Supabase (deduplication via external_id)
  4. Print a summary report

Usage:
    python -m scraper.pipeline.ingest            # Full 5,000-job run
    python -m scraper.pipeline.ingest --test     # 20-job smoke test
    python -m scraper.pipeline.ingest --max 500  # Custom count
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict

# Allow running as `python -m scraper.pipeline.ingest` from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scraper.config import ScraperConfig
from scraper.client.apify_scraper import ApifyJobStreetScraper
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Keywords covering all 4 TechGap tracks
# ---------------------------------------------------------------------------
# CS-IS, CS-GD, IT-WD, IT-NT
KEYWORDS = [
    # IT-WD track
    "web developer",
    "frontend developer",
    "backend developer",
    "full stack developer",
    "react developer",
    "nodejs developer",
    # IT-NT track
    "network engineer",
    "network administrator",
    "systems administrator",
    "cybersecurity analyst",
    "IT support",
    # CS-IS track
    "software engineer",
    "software developer",
    "data analyst",
    "business analyst",
    "information systems",
    # CS-GD track
    "game developer",
    "unity developer",
    "UI UX designer",
    "graphic designer",
]


def get_supabase_client(config: ScraperConfig) -> Client:
    """Create and verify the Supabase connection."""
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in your .env file."
        )
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


def upsert_jobs(supabase: Client, records: List[dict]) -> Dict:
    """
    Upsert job records into jobs_raw table.
    Deduplication key: (source, external_id).

    Returns a summary dict: {inserted, updated, skipped, errors}
    """
    summary = {"inserted": 0, "skipped": 0, "errors": 0, "total_sent": len(records)}

    if not records:
        logger.warning("No records to upsert.")
        return summary

    # Supabase upsert with on_conflict = external_id
    # Records with a matching external_id will be updated; new ones inserted.
    try:
        response = (
            supabase.table("jobs_raw")
            .upsert(records, on_conflict="source, external_id", ignore_duplicates=False)
            .execute()
        )
        # Supabase Python client v2: response.data is the list of upserted rows
        upserted_count = len(response.data) if response.data else 0
        summary["inserted"] = upserted_count
        logger.debug(f"Upsert response: {upserted_count} rows affected")

    except Exception as exc:
        logger.error(f"Supabase upsert failed: {exc}")
        summary["errors"] = len(records)

    return summary


def run_pipeline(max_items: int, test_mode: bool = False) -> None:
    """Main pipeline entry point."""
    config = ScraperConfig()

    if not config.APIFY_API_TOKEN:
        logger.error(
            "❌ APIFY_API_TOKEN is not set in your .env file.\n"
            "   Sign up at https://apify.com and get your token from:\n"
            "   https://console.apify.com/account/integrations"
        )
        sys.exit(1)

    # --- Setup ---
    logger.info("=" * 60)
    logger.info("  TechGap — Apify → Supabase Ingestion Pipeline")
    logger.info("=" * 60)
    logger.info(f"  Mode:      {'🧪 TEST (20 jobs)' if test_mode else '🚀 FULL RUN'}")
    logger.info(f"  Target:    {max_items:,} jobs")
    logger.info(f"  Actor:     {config.APIFY_ACTOR_ID}")
    logger.info(f"  Country:   {config.APIFY_COUNTRY.upper()}")
    logger.info(f"  Keywords:  {len(KEYWORDS)}")
    logger.info("=" * 60)

    # --- 1. Run the Apify scraper ---
    scraper = ApifyJobStreetScraper(
        api_token=config.APIFY_API_TOKEN,
        actor_id=config.APIFY_ACTOR_ID,
    )

    start_time = datetime.now()
    keywords_to_use = KEYWORDS[:3] if test_mode else KEYWORDS  # Use fewer keywords in test mode

    logger.info(f"\n📡 Starting Apify actor runs ({len(keywords_to_use)} keywords)...\n")
    records = scraper.run(
        keywords=keywords_to_use,
        country=config.APIFY_COUNTRY,
        max_items=max_items,
        max_post_age_days=config.MAX_POST_AGE_DAYS,
    )

    elapsed_scrape = (datetime.now() - start_time).total_seconds()
    logger.info(f"\n✅ Scraping complete: {len(records)} records in {elapsed_scrape:.1f}s\n")

    if not records:
        logger.error("❌ No records returned. Check your Apify token and actor config.")
        sys.exit(1)

    # --- 1.5 Deduplicate locally ---
    # The actor might return the same job multiple times for different keywords.
    unique_records = {}
    for r in records:
        if r.get("external_id"):
            unique_records[r["external_id"]] = r
    
    deduped_records = list(unique_records.values())
    if len(deduped_records) < len(records):
        logger.info(f"🧹 Removed {len(records) - len(deduped_records)} duplicate records locally.")

    # --- 2. Upsert into Supabase ---
    logger.info(f"💾 Connecting to Supabase and upserting {len(deduped_records)} unique records...")
    supabase = get_supabase_client(config)
    summary = upsert_jobs(supabase, deduped_records)

    elapsed_total = (datetime.now() - start_time).total_seconds()

    # --- 3. Print Report ---
    logger.info("\n" + "=" * 60)
    logger.info("  📊 INGESTION REPORT")
    logger.info("=" * 60)
    logger.info(f"  Records scraped:   {len(records):>6,}")
    logger.info(f"  Records sent to DB:{summary['total_sent']:>6,}")
    logger.info(f"  Successfully saved:{summary['inserted']:>6,}")
    logger.info(f"  Errors:            {summary['errors']:>6,}")
    logger.info(f"  Total time:        {elapsed_total:>6.1f}s")
    logger.info("=" * 60)

    if test_mode:
        logger.info("\n💡 Test mode complete. Run without --test for the full 5,000-job collection.")
        logger.info("   Check your Supabase Table Editor to verify the inserted rows.\n")

    if summary["errors"] > 0:
        logger.warning(f"⚠️  {summary['errors']} records had errors. Check logs above.")
        sys.exit(1)

    logger.info("\n🎉 Pipeline finished successfully!\n")


def main():
    parser = argparse.ArgumentParser(
        description="TechGap: Apify → Supabase ETL ingestion pipeline"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run a quick 20-job smoke test (3 keywords, 20 total results)"
    )
    parser.add_argument(
        "--max", type=int, default=None,
        help="Override the max items to collect (default: 20 for --test, 5000 for full run)"
    )
    args = parser.parse_args()

    if args.test:
        max_items = args.max or 20
    else:
        max_items = args.max or 5000

    run_pipeline(max_items=max_items, test_mode=args.test)


if __name__ == "__main__":
    main()
