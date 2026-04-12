"""TechGap Scraper — Configuration via .env"""

from pydantic_settings import BaseSettings


class ScraperConfig(BaseSettings):
    """All scraper settings loaded from .env file."""

    # --- Apify (Primary Provider) ---
    APIFY_API_TOKEN: str = ""
    APIFY_ACTOR_ID: str = "shahidirfan/jobstreet-scraper"
    APIFY_COUNTRY: str = "ph"
    APIFY_MAX_ITEMS: int = 5000  # Target for full run

    # --- Supabase ---
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""  # Must be legacy JWT key (eyJhb...), not sb_publishable_ format

    # --- Scraper Behavior ---
    MAX_POST_AGE_DAYS: int = 180

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
