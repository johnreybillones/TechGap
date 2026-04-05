"""TechGap Scraper — Configuration via .env"""

from pydantic_settings import BaseSettings
from typing import Literal


class ScraperConfig(BaseSettings):
    """All scraper settings loaded from .env file."""

    # --- Provider Toggle ---
    ACTIVE_PROVIDER: Literal["APIFY", "BRIGHTDATA", "SCRAPERAPI"] = "APIFY"

    # --- Apify (Primary Provider) ---
    APIFY_API_TOKEN: str = ""
    APIFY_ACTOR_ID: str = "shahidirfan/jobstreet-scraper"
    APIFY_COUNTRY: str = "ph"
    APIFY_MAX_ITEMS: int = 5000  # Target for full run

    # --- Bright Data (now deprecated — kept for reference) ---
    BD_API_TOKEN: str = ""
    BD_ZONE: str = "web_unlocker1"

    # --- ScraperAPI (fallback if needed) ---
    SCRAPERAPI_KEY: str = ""

    # --- Supabase ---
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # --- Scraper Behavior ---
    CONCURRENT_REQUESTS: int = 5
    MAX_POST_AGE_DAYS: int = 180

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
