"""
HTTP client singleton for connection pooling across the application.

Provides a shared aiohttp connector with optimized settings for performance.
"""

import aiohttp
from aiohttp import TCPConnector

from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager


class _HTTPClient:
    """
    Singleton HTTP client for connection pooling.

    Provides a shared TCP connector with optimized settings for high-performance
    HTTP operations across the application.
    """

    def __init__(self):
        """Initialize HTTP client with pooled connector."""
        super().__init__()
        self._connector = None

    def get_connector(self) -> TCPConnector:
        """
        Get the shared TCP connector.

        Creates the connector on first access for lazy initialization.
        Requires an active event loop.
        """
        if self._connector is None or self._connector.closed:
            try:
                self._connector = aiohttp.TCPConnector(
                    limit=100,  # Total connection pool size
                    limit_per_host=50,  # Per-host connection limit
                    keepalive_timeout=30,  # Keep connections alive for 30 seconds
                    enable_cleanup_closed=True,  # Clean up closed connections
                    ttl_dns_cache=300,  # DNS cache TTL (5 minutes)
                    use_dns_cache=True,  # Enable DNS caching
                )
            except RuntimeError as e:
                if "no running event loop" in str(e):
                    raise RuntimeError("HTTPClient.get_connector() requires an active event loop. Call this method from within an async context.") from e
                raise
        return self._connector

    def create_session(self, **kwargs) -> aiohttp.ClientSession:
        """
        Create a new client session with the shared connector.

        Args:
            **kwargs: Additional arguments for ClientSession

        Returns:
            Configured ClientSession with shared connector
        """
        session_kwargs = {"connector": self.get_connector()}
        session_kwargs.update(kwargs)
        return aiohttp.ClientSession(**session_kwargs)

    async def close(self):
        """
        Close the HTTP client and clean up resources.

        Should be called during application shutdown.
        """
        if self._connector is not None and not self._connector.closed:
            await self._connector.close()
            self._connector = None

    @property
    def is_closed(self) -> bool:
        """Check if the HTTP client is closed."""
        return self._connector is not None and self._connector.closed

    def get_connection_stats(self) -> dict:
        """
        Get connection pool statistics.

        Returns:
            Dictionary with connection pool statistics
        """
        if self._connector is None:
            return {"status": "not_initialized"}

        return {
            "limit": self._connector.limit,
            "limit_per_host": self._connector.limit_per_host,
            "keepalive_timeout": self._connector.keepalive_timeout,
            "is_closed": self._connector.closed,
        }


http_client = _HTTPClient()
singleton_manager.register(http_client)
