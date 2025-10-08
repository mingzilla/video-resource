"""
AsyncDnsValidator - Concurrent DNS domain validation utility

IMPORTANT: Create this as a singleton in your system so that all services share
the same concurrent limit (semaphore). This ensures system-wide DNS request throttling.

If multiple services need DNS validation:
1. Create a module-level singleton:
   # dns_validator_singleton.py
   from shared_utils.external.dns.async_dns_validator import AsyncDnsValidator
   dns_validator = AsyncDnsValidator()

2. Import and use in services:
   from shared_utils.external.dns.dns_validator_singleton import dns_validator
   results = await dns_validator.validate_domains(urls)

This prevents each service from creating its own validator with separate semaphores,
which would allow total concurrent DNS requests to exceed the intended limit.
"""

import asyncio
import logging
from shared_utils.external.dns.url_validator_util import UrlValidatorUtil


logger = logging.getLogger(__name__)


class AsyncDnsValidator:
    def __init__(self, max_concurrent: int = 1000):
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def validate_domains(self, urls: list[str]) -> dict[str, bool]:
        """Validate multiple domains concurrently and return existence status.

        Args:
            urls: List of URLs/domains to validate (may contain duplicates/None)

        Returns:
            Dictionary mapping each unique URL to its DNS existence status
            Example: {"example.com": True, "invalid.xyz": False}
        """
        unique_urls = list(set(url for url in urls if url and url.strip()))

        if not unique_urls:
            return {}

        logger.info(f"Validating {len(unique_urls)} unique domains (from {len(urls)} total)")

        async def check_one(url: str) -> tuple[str, bool]:
            async with self._semaphore:
                exists = await UrlValidatorUtil.domain_exists(url)
                return (url, exists)

        tasks = [check_one(url) for url in unique_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        domain_status = {}
        for item in results:
            if isinstance(item, Exception):
                logger.warning(f"DNS validation exception: {item}")
                continue
            url, exists = item
            domain_status[url] = exists

        logger.info(f"Validated {len(domain_status)} domains successfully")
        return domain_status
