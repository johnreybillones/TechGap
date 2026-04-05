"""
TechGap Scraper — Hybrid API Client
Seamlessly switches between Bright Data and ScraperAPI based on .env config.
"""

import httpx
import asyncio
import logging

from scraper.config import ScraperConfig

logger = logging.getLogger(__name__)


class ScraperAPIError(Exception):
    """Raised when the scraping API returns an error."""
    pass


class HybridScraperClient:
    """
    Fetches raw HTML from JobStreet via external Scraping APIs.

    Phase 1 (Bright Data trial): Uses Web Unlocker REST API
    Phase 2 (Post-trial):        Uses ScraperAPI REST endpoint

    Switching is controlled by ACTIVE_PROVIDER in .env
    """

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.provider = config.ACTIVE_PROVIDER
        self._request_count = 0
        logger.info(f"Initialized HybridScraperClient with provider: {self.provider}")

    async def fetch_html(self, target_url: str, retries: int = 3) -> str:
        """
        Fetch the fully-rendered HTML of a URL via the active scraping provider.

        Args:
            target_url: The JobStreet URL to scrape
            retries: Number of retry attempts on failure

        Returns:
            Raw HTML string of the page

        Raises:
            ScraperAPIError: If all retry attempts fail
        """
        last_error = None

        for attempt in range(1, retries + 1):
            try:
                if self.provider == "BRIGHTDATA":
                    html = await self._fetch_via_brightdata(target_url)
                elif self.provider == "SCRAPERAPI":
                    html = await self._fetch_via_scraperapi(target_url)
                else:
                    raise ValueError(f"Unknown provider: {self.provider}")

                self._request_count += 1

                # Basic validation: HTML should contain something meaningful
                if not html or len(html) < 500:
                    raise ScraperAPIError(
                        f"Response too short ({len(html) if html else 0} chars) — "
                        f"possible block or empty page"
                    )

                if attempt > 1:
                    logger.info(f"Succeeded on attempt {attempt}")

                return html

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_error = e
                wait_time = 5 * (2 ** (attempt - 1))  # 5s, 10s, 20s
                logger.warning(
                    f"Attempt {attempt}/{retries} failed ({type(e).__name__}). "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                last_error = e
                wait_time = 10 * attempt
                logger.warning(
                    f"Attempt {attempt}/{retries}: HTTP {e.response.status_code}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

            except ScraperAPIError as e:
                last_error = e
                wait_time = 10 * attempt
                logger.warning(
                    f"Attempt {attempt}/{retries}: {e}. Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

        raise ScraperAPIError(
            f"Failed to fetch {target_url} after {retries} attempts. "
            f"Last error: {last_error}"
        )

    async def _fetch_via_brightdata(self, target_url: str) -> str:
        """
        Fetch via Bright Data Web Unlocker REST API.

        Uses POST to https://api.brightdata.com/request with Bearer token auth,
        matching the user's confirmed working curl command.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.BD_API_TOKEN}",
        }
        payload = {
            "zone": self.config.BD_ZONE,
            "url": target_url,
            "format": "raw",
        }

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(90.0, connect=30.0),
        ) as client:
            response = await client.post(
                "https://api.brightdata.com/request",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.text

    async def _fetch_via_scraperapi(self, target_url: str) -> str:
        """Fetch via ScraperAPI REST endpoint."""
        params = {
            "api_key": self.config.SCRAPERAPI_KEY,
            "url": target_url,
            "render": "true",  # Ensure JS is executed (needed for __NEXT_DATA__)
        }

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(90.0, connect=30.0),
        ) as client:
            response = await client.get(
                "http://api.scraperapi.com",
                params=params,
            )
            response.raise_for_status()
            return response.text

    @property
    def request_count(self) -> int:
        """Total requests made in this session."""
        return self._request_count
