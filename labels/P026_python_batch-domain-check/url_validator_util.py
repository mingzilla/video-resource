import aiodns
import logging
from typing import Optional


logger = logging.getLogger(__name__)


class UrlValidatorUtil:
    _resolver = aiodns.DNSResolver()

    @staticmethod
    async def domain_exists(url: Optional[str]) -> bool:
        """
        Check if a domain exists by verifying DNS resolution.
        Fast, lightweight, and not affected by bot protection.
        Uses aiodns for true async DNS resolution.

        Returns:
            True if domain resolves via DNS (domain exists)
            False if domain does not resolve (domain doesn't exist)
        """
        if not url or not url.strip():
            return False

        domain = url.strip()
        domain = domain.replace('https://', '').replace('http://', '').split('/')[0]

        try:
            await UrlValidatorUtil._resolver.gethostbyname(domain, aiodns.socket.AF_INET)
            logger.debug(f"Domain {domain} resolves via DNS")
            return True
        except aiodns.error.DNSError:
            logger.debug(f"Domain {domain} does not resolve via DNS")
            return False
