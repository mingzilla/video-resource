"""
Health service for coordinating system health checks.

Aggregates health status from all singleton services and components.
"""

from typing import Dict

from github_mingzilla.llm_mcp.clients.llm_client import llm_client
from github_mingzilla.llm_mcp.clients.mcp_client import mcp_client
from github_mingzilla.llm_mcp.repositories.chat_history_repository import chat_history_repo
from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager


class _HealthService:
    """
    Service for health check coordination.
    """

    def __init__(self):
        """Initialize health service with singleton dependencies."""
        self.llm_client = llm_client
        self.mcp_client = mcp_client
        self.chat_history_repo = chat_history_repo

    async def get_comprehensive_health_status(self) -> Dict:
        """
        Get comprehensive health status for all system components.

        Returns:
            Dictionary with detailed health information
        """
        health_status = {
            "status": "healthy",
            "components": {},
        }

        # Test LLM client health
        llm_healthy = await self._check_llm_health(health_status)

        # Test MCP client health
        mcp_healthy = await self._check_mcp_health(health_status)

        # Test repository health
        repo_healthy = self._check_repository_health(health_status)

        # Calculate overall health
        overall_healthy = llm_healthy and mcp_healthy and repo_healthy
        health_status["status"] = "healthy" if overall_healthy else "unhealthy"
        health_status["overall_healthy"] = overall_healthy

        return health_status

    async def get_basic_health_status(self) -> Dict:
        """
        Get basic health status (faster check).

        Returns:
            Simple health status dictionary
        """
        try:
            # Quick repository check
            repo_working = self.chat_history_repo is not None

            return {"status": "healthy" if repo_working else "unhealthy", "timestamp": self._get_current_timestamp(), "basic_check": True}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": self._get_current_timestamp(), "basic_check": True}

    async def _check_llm_health(self, health_status: Dict) -> bool:
        """
        Check LLM client health and update status.

        Args:
            health_status: Health status dictionary to update

        Returns:
            True if LLM client is healthy
        """
        try:
            llm_healthy = await self.llm_client.test_connection()
            health_status["components"]["llm"] = {
                "status": "healthy" if llm_healthy else "unhealthy",
                "details": "LLM client connection",
            }
            return llm_healthy
        except Exception as e:
            health_status["components"]["llm"] = {
                "status": "error",
                "details": f"LLM client error: {str(e)}",
            }
            return False

    async def _check_mcp_health(self, health_status: Dict) -> bool:
        """
        Check MCP client health and update status.

        Args:
            health_status: Health status dictionary to update

        Returns:
            True if MCP client is healthy
        """
        try:
            mcp_healthy = await self.mcp_client.test_connection()

            # Try to get server URL for details (handle potential AttributeError)
            try:
                server_details = f"MCP server at {self.mcp_client.server_url}"
            except AttributeError:
                server_details = "MCP client connection"

            health_status["components"]["mcp"] = {
                "status": "healthy" if mcp_healthy else "unhealthy",
                "details": server_details,
            }
            return mcp_healthy
        except Exception as e:
            health_status["components"]["mcp"] = {
                "status": "error",
                "details": f"MCP client error: {str(e)}",
            }
            return False

    def _check_repository_health(self, health_status: Dict) -> bool:
        """
        Check repository health and update status.

        Args:
            health_status: Health status dictionary to update

        Returns:
            True if repository is healthy
        """
        try:
            # Basic repository functionality test
            session_count = len(self.chat_history_repo.get_all_session_ids())

            health_status["components"]["repository"] = {
                "status": "healthy",
                "details": f"Chat history repository operational (active sessions: {session_count})",
            }
            return True
        except Exception as e:
            health_status["components"]["repository"] = {
                "status": "error",
                "details": f"Repository error: {str(e)}",
            }
            return False

    async def get_component_health(self, component: str) -> Dict:
        """
        Get health status for a specific component.

        Args:
            component: Component name ('llm', 'mcp', or 'repository')

        Returns:
            Component-specific health status

        Raises:
            ValueError: If component name is invalid
        """
        valid_components = ["llm", "mcp", "repository"]
        if component not in valid_components:
            raise ValueError(f"Invalid component. Must be one of: {valid_components}")

        if component == "llm":
            health_status = {"components": {}}
            healthy = await self._check_llm_health(health_status)
            return {"component": component, "healthy": healthy, **health_status["components"]["llm"]}

        elif component == "mcp":
            health_status = {"components": {}}
            healthy = await self._check_mcp_health(health_status)
            return {"component": component, "healthy": healthy, **health_status["components"]["mcp"]}

        elif component == "repository":
            health_status = {"components": {}}
            healthy = self._check_repository_health(health_status)
            return {"component": component, "healthy": healthy, **health_status["components"]["repository"]}

    def get_health_summary(self) -> Dict:
        """
        Get a quick health summary without detailed checks.

        Returns:
            Basic health summary
        """
        return {"service": "health_service", "status": "operational", "components_available": ["llm", "mcp", "repository"], "check_endpoints": {"comprehensive": "/health", "basic": "/health/basic", "component": "/health/{component}"}}

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp for health checks.

        Returns:
            ISO formatted timestamp string
        """
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


# Module-level singleton instance
health_service = _HealthService()
singleton_manager.register(health_service)
