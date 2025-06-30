"""
Multi-MCP Client Manager

Manages connections to multiple MCP servers and routes tool calls appropriately.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx


class MultiMcpClient:
    """Manages connections to multiple MCP servers and routes tool calls"""

    def __init__(self, base_url_mapping: Dict[str, str] = None):
        """
        Initialize multi-MCP client with server mappings

        Args:
            base_url_mapping: Mapping of server names to base URLs
        """
        self.logger = logging.getLogger(__name__)

        # Default server configuration
        self.server_config = base_url_mapping or {"api_config": "http://localhost:8000/mcp/", "calculator": "http://localhost:8010/mcp/"}

        # Tool routing configuration - maps tool names to server names
        self.tool_routing = {
            # API Config tools -> api_config server
            "create_api_config": "api_config",
            "get_api_config": "api_config",
            "get_all_api_configs": "api_config",
            "update_api_config": "api_config",
            "delete_api_config": "api_config",
            # Calculator tools -> calculator server
            "add": "calculator",
            "multiply": "calculator",
        }

        # HTTP client for making requests
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # Cache for available tools
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp = 0
        self._cache_ttl = 60  # Cache for 60 seconds

    async def discover_tools(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Discover tools from all connected MCP servers

        Args:
            force_refresh: Force refresh of tools cache

        Returns:
            List of all available tools from all servers
        """
        import time

        current_time = time.time()

        # Use cached tools if available and not expired
        if not force_refresh and self._tools_cache and current_time - self._cache_timestamp < self._cache_ttl:
            return self._tools_cache

        all_tools = []

        # Discover tools from each server
        for server_name, base_url in self.server_config.items():
            try:
                server_tools = await self._discover_tools_from_server(server_name, base_url)
                all_tools.extend(server_tools)
                self.logger.info(f"Discovered {len(server_tools)} tools from {server_name} server")
            except Exception as e:
                self.logger.warning(f"Failed to discover tools from {server_name} server at {base_url}: {e}")

        # Update cache
        self._tools_cache = all_tools
        self._cache_timestamp = current_time

        self.logger.info(f"Total tools discovered from all servers: {len(all_tools)}")
        return all_tools

    async def _discover_tools_from_server(self, server_name: str, base_url: str) -> List[Dict[str, Any]]:
        """
        Discover tools from a specific MCP server

        Args:
            server_name: Name of the server
            base_url: Base URL of the MCP server

        Returns:
            List of tools from this server
        """
        try:
            url = f"{base_url.rstrip('/')}/tools"
            headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            tools = data.get("tools", [])

            # Add server metadata to each tool
            for tool in tools:
                tool["_server"] = server_name
                tool["_server_url"] = base_url

            return tools

        except Exception as e:
            self.logger.error(f"Error discovering tools from {server_name}: {e}")
            raise

    async def execute_tool(self, tool_name: str, tool_arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by routing to the appropriate MCP server

        Args:
            tool_name: Name of the tool to execute
            tool_arguments: Arguments for the tool

        Returns:
            Tool execution result
        """
        # Find the server for this tool
        server_name = self.tool_routing.get(tool_name)
        if not server_name:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Get server URL
        base_url = self.server_config.get(server_name)
        if not base_url:
            raise ValueError(f"No server configured for: {server_name}")

        # Execute tool on the appropriate server
        try:
            result = await self._execute_tool_on_server(server_name, base_url, tool_name, tool_arguments)
            self.logger.info(f"Successfully executed {tool_name} on {server_name} server")
            return result

        except Exception as e:
            self.logger.error(f"Failed to execute {tool_name} on {server_name}: {e}")
            raise

    async def _execute_tool_on_server(self, server_name: str, base_url: str, tool_name: str, tool_arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on a specific MCP server

        Args:
            server_name: Name of the server
            base_url: Base URL of the MCP server
            tool_name: Name of the tool
            tool_arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            url = f"{base_url.rstrip('/')}/call"

            payload = {"method": "tools/call", "params": {"name": tool_name, "arguments": tool_arguments}}

            headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
            response = await self.http_client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Extract result from MCP response format
            if "result" in data:
                return data["result"]
            else:
                return data

        except Exception as e:
            self.logger.error(f"Error executing {tool_name} on {server_name}: {e}")
            raise

    async def check_server_health(self, server_name: str = None) -> Dict[str, bool]:
        """
        Check health status of MCP servers

        Args:
            server_name: Check specific server, or all if None

        Returns:
            Dictionary mapping server names to health status
        """
        health_status = {}

        servers_to_check = {server_name: self.server_config[server_name]} if server_name else self.server_config

        # Check each server
        tasks = []
        for name, url in servers_to_check.items():
            tasks.append(self._check_single_server_health(name, url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, (name, _) in enumerate(servers_to_check.items()):
            health_status[name] = not isinstance(results[i], Exception) and results[i]

        return health_status

    async def _check_single_server_health(self, server_name: str, base_url: str) -> bool:
        """
        Check health of a single MCP server

        Args:
            server_name: Name of the server
            base_url: Base URL of the server

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # Try to discover tools as a health check
            url = f"{base_url.rstrip('/')}/tools"
            headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
            response = await self.http_client.get(url, headers=headers, timeout=5.0)
            response.raise_for_status()
            return True

        except Exception as e:
            self.logger.warning(f"Health check failed for {server_name}: {e}")
            return False

    async def get_tools_by_server(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get tools grouped by server

        Returns:
            Dictionary mapping server names to their tools
        """
        all_tools = await self.discover_tools()

        tools_by_server = {}
        for tool in all_tools:
            server_name = tool.get("_server", "unknown")
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            tools_by_server[server_name].append(tool)

        return tools_by_server

    async def close(self):
        """Close HTTP client and cleanup resources"""
        if self.http_client:
            await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
