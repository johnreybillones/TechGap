"""
TechGap — Apify JobStreet Scraper Client
=========================================
Uses the `apify-client` SDK to run the `shahidirfan/jobstreet-scraper` actor
and retrieve structured job listing data for the Philippines market.

Actor URL: https://apify.com/shahidirfan/jobstreet-scraper
Cost:       ~$1.00 per 1,000 results  (Free tier = $5 credit)
Target:     5,000 jobs for thesis pipeline
"""

import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from apify_client import ApifyClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# JobStreet → jobs_raw field mapping
# ---------------------------------------------------------------------------
# The actor returns camelCase keys. This dict maps them to our DB column names.
# Fields not listed here are either not available or handled separately.
FIELD_MAP = {
    # Apify actor key    →   jobs_raw column
    "id":                "external_id",    
    "title":             "job_title",
    "description_text":  "description",
    "workType":          "contract_type",
    "company":           "company_name",
    "location":          "location",
    "classification":    "classification",
    "url":               "source_url",
    "postedAt_iso":      "posted_at",
}


class ApifyJobStreetScraper:
    """
    Wraps the Apify client to run the JobStreet actor and return
    records ready for insertion into the `jobs_raw` Supabase table.
    """

    def __init__(self, api_token: str, actor_id: str = "shahidirfan/jobstreet-scraper"):
        if not api_token:
            raise ValueError(
                "APIFY_API_TOKEN is missing. Add it to your .env file.\n"
                "Get your token at: https://console.apify.com/account/integrations"
            )
        self.client = ApifyClient(api_token)
        self.actor_id = actor_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        keywords: List[str],
        country: str = "ph",
        max_items: int = 100,
        max_post_age_days: int = 180,
    ) -> List[dict]:
        """
        Run the ActorJobStreet actor for each keyword and aggregate results.

        Args:
            keywords:         Search terms, e.g. ["software engineer", "data analyst"]
            country:          JobStreet country code — always "ph" for Philippines
            max_items:        Total results cap across all keywords
            max_post_age_days: Drop jobs older than this (server-side filter not always reliable)

        Returns:
            List of dicts mapped to jobs_raw columns, ready for Supabase upsert.
        """
        all_results: List[dict] = []
        per_keyword = max(10, max_items // len(keywords))

        for keyword in keywords:
            logger.info(f"  ▶  Scraping keyword: '{keyword}' (up to {per_keyword} results)...")
            try:
                raw_items = self._run_actor(keyword, country, per_keyword)
            except Exception as exc:
                logger.error(f"  ✗  Actor run failed for '{keyword}': {exc}")
                continue

            for item in raw_items:
                mapped = self._map_record(item)
                if mapped and self._is_within_age(mapped, max_post_age_days):
                    all_results.append(mapped)

            logger.info(f"  ✓  {len(raw_items)} raw → {len(all_results)} total mapped so far")

            if len(all_results) >= max_items:
                logger.info(f"  ■  Reached max_items cap ({max_items}). Stopping.")
                break

        return all_results[:max_items]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run_actor(self, keyword: str, country: str, max_items: int) -> List[dict]:
        """
        Start one actor run and wait for it to finish, then fetch items.
        This is synchronous (Apify client blocks until done).
        """
        run_input = {
            "keyword": keyword,
            "country": country,
            "results_wanted": max_items,   # Actor's actual field name (NOT maxItems)
            "posted_date": "anytime",       # Options: anytime, 24h, 7d, 30d
        }

        logger.debug(f"    Starting actor run: {self.actor_id}, input={run_input}")

        # call() blocks until the run finishes — no polling needed
        run = self.client.actor(self.actor_id).call(run_input=run_input)

        if not run:
            raise RuntimeError(f"Actor returned no run object for keyword='{keyword}'")

        run_status = run.get("status", "UNKNOWN")
        if run_status != "SUCCEEDED":
            raise RuntimeError(
                f"Actor run ended with status '{run_status}' for keyword='{keyword}'. "
                f"Check Apify console: https://console.apify.com/actors/runs/{run.get('id')}"
            )

        # Fetch all items from the dataset
        dataset_id = run["defaultDatasetId"]
        items = list(
            self.client.dataset(dataset_id).iterate_items()
        )
        logger.debug(f"    Retrieved {len(items)} items from dataset {dataset_id}")
        return items

    def _map_record(self, item: dict) -> Optional[dict]:
        """
        Transform a raw Apify actor output item into a jobs_raw-compatible dict.
        Returns None if the record is missing critical fields.
        """
        # Require at minimum: a job ID and a description
        if not item.get("jobId") and not item.get("id"):
            logger.debug(f"    Skipping record with no jobId: {list(item.keys())}")
            return None

        if not item.get("description_text") and not item.get("description"):
            logger.debug(f"    Skipping record with no description_text/description: {item.get('id') or item.get('jobId')}")
            return None

        mapped: dict = {
            "source": "jobstreet",
            "seniority_level": None,      # Populated by Week 2 NLP pipeline
            "track_alignment": None,       # Populated by Week 2 inference
            "salary_currency": "PHP",
            "description_embedding": None, # Populated by Week 2 SBERT
            "raw_json": item,              # Full original payload for auditability
        }

        # Map standard fields
        for actor_key, db_col in FIELD_MAP.items():
            value = item.get(actor_key)
            if value is not None:
                mapped[db_col] = value

        # Fallback: some actor versions use "id" instead of "jobId"
        if not mapped.get("external_id"):
            mapped["external_id"] = str(item.get("id", ""))

        # Normalise company name (actor may return a dict or a string)
        company = mapped.get("company_name")
        if isinstance(company, dict):
            mapped["company_name"] = company.get("name") or company.get("displayName", "")

        # Normalise location (actor may return a dict or a string)
        location = mapped.get("location")
        if isinstance(location, dict):
            mapped["location"] = (
                location.get("city")
                or location.get("area")
                or location.get("label", "")
            )

        # Normalise posted_at to ISO 8601 string
        posted = mapped.get("posted_at")
        if posted:
            if isinstance(posted, (int, float)):
                # Unix timestamp in milliseconds
                dt = datetime.fromtimestamp(posted / 1000, tz=timezone.utc)
                mapped["posted_at"] = dt.isoformat()
            elif isinstance(posted, str) and posted.strip():
                # Already a string — pass through
                mapped["posted_at"] = posted.strip()
        else:
            mapped["posted_at"] = None

        # Parse string salary if available e.g., "₱40,000 – ₱60,000 per month"
        salary_str = item.get("salary")
        if isinstance(salary_str, str):
            # Extract all numbers from string, remove commas
            nums = re.findall(r'\d+(?:,\d+)*', salary_str)
            nums = [float(n.replace(',', '')) for n in nums]
            if len(nums) == 1:
                mapped["salary_min"] = nums[0]
                mapped["salary_max"] = nums[0]
            elif len(nums) >= 2:
                mapped["salary_min"] = nums[0]
                mapped["salary_max"] = nums[1]
            else:
                mapped["salary_min"] = None
                mapped["salary_max"] = None
        else:
            mapped["salary_min"] = None
            mapped["salary_max"] = None

        return mapped

    @staticmethod
    def _is_within_age(record: dict, max_days: int) -> bool:
        """Return True if the posting is within max_days of today."""
        posted = record.get("posted_at")
        if not posted:
            return True  # No date → keep it (do not reject on unknown)

        try:
            if isinstance(posted, str):
                # Handle offsets like "2024-11-15T10:00:00+08:00"
                dt = datetime.fromisoformat(posted)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            else:
                return True  # Unknown type → keep

            cutoff = datetime.now(tz=timezone.utc) - timedelta(days=max_days)
            return dt >= cutoff
        except Exception:
            return True  # Parse error → keep (don't discard data)
