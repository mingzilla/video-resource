from aiohttp import TCPConnector


class HttpUtil:
    @staticmethod
    def create_pooled_connector() -> TCPConnector:
        import aiohttp

        return aiohttp.TCPConnector(
            limit=100,
            limit_per_host=50,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )
