import asyncio
import json
from typing import Any, Dict, List, Optional

from github_mingzilla.llm_mcp.config import load_enabled_mcp_servers
from github_mingzilla.llm_mcp.mcp_clients.single_server_mcp_client import SingleServerMCPClient
from github_mingzilla.llm_mcp.models import ApiChatMessage, DomainMcpTool, DomainToolExecutionRequest, DomainToolSelection
from github_mingzilla.llm_mcp.service_manager.interfaces import ClosableService
from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager


class _MCPClient(ClosableService):
    """Dynamic multi-MCP client that supports any number of MCP servers via configuration."""

    def __init__(self):
        """Initialize MCP client with dynamic server configuration."""
        # Load enabled server configuration
        self._server_config = load_enabled_mcp_servers()

        # Dynamic client management
        self._mcp_clients: Dict[str, SingleServerMCPClient] = {}

    async def get_filtered_tools(self, selected_tools: Optional[List[DomainToolSelection]]) -> List[DomainMcpTool]:
        """Get filtered tools based on ToolSelection objects."""
        if not selected_tools:
            return []

        mcp_tools = await self.discover_tools()

        filtered_tools = []
        for tool in mcp_tools:
            for selection in selected_tools:
                # Handle both DomainMcpTool objects and dict fallback
                tool_name = tool.name if hasattr(tool, "name") else tool.get("name") if isinstance(tool, dict) else None
                tool_server = tool.server if hasattr(tool, "server") else tool.get("server") if isinstance(tool, dict) else None

                if tool_name and tool_name == selection.name:
                    if selection.server is None or tool_server == selection.server:
                        filtered_tools.append(tool)
                        break
        return filtered_tools

    async def discover_tools(self) -> List[DomainMcpTool]:
        """
        Discover available tools from all MCP servers.
        Returns:
            List of tool definitions from all servers
        """
        all_tools = []

        # Discover tools from all enabled servers
        for server_name, server_config in self._server_config.items():
            try:
                client = await self._get_or_create_client(server_name)

                if client:
                    server_tools = await client.discover_tools()

                    # Convert to DomainMcpTool objects with server metadata using boundary model
                    for tool_item in server_tools:
                        mcp_tool = DomainMcpTool.from_dict(tool_item, server=server_name, server_url=server_config["url"], server_description=server_config.get("description", ""))
                        all_tools.append(mcp_tool)
                    print(f"Found {len(server_tools)} tools from {server_name} server")
                else:
                    print(f"Failed to connect to {server_name} server")

            except Exception as e:
                print(f"Error discovering tools from {server_name} server: {e}")

        print(f"Total tools discovered: {len(all_tools)} from {len(self._server_config)} servers")
        return all_tools

    async def _get_or_create_client(self, server_name: str):
        """Get existing client or create new one for the specified server."""
        if server_name not in self._mcp_clients:
            self._mcp_clients[server_name] = await self._create_mcp_client(server_name)
        return self._mcp_clients[server_name]

    async def _create_mcp_client(self, server_name: str) -> SingleServerMCPClient:
        """Create an individual MCP client for a specific server."""
        try:
            # Create a simple MCPClient that connects to a specific server
            # Get server configuration
            if server_name not in self._server_config:
                raise ValueError(f"Unknown server: {server_name}")

            server_config = self._server_config[server_name]
            server_url = server_config["url"]

            # Create client for the specified server
            client = SingleServerMCPClient(server_name, server_url)

            if await client.connect():
                return client
            else:
                return None

        except Exception as e:
            print(f"Failed to create MCP client for {server_name}: {e}")
            return None

    async def execute_tools_parallel(self, tool_execution_data: List[DomainToolExecutionRequest]) -> List[ApiChatMessage]:
        """
        Execute multiple tools in parallel and return ChatMessage objects.

        Args:
            tool_execution_data: List of DomainToolExecutionRequest objects with tool execution details

        Returns:
            List of ApiChatMessage objects with role='tool'
        """

        async def execute_single_tool(tool_data: DomainToolExecutionRequest) -> ApiChatMessage:
            """Execute a single tool call and return the result as ChatMessage."""
            try:
                tool_name = tool_data.name
                # Use the typed method to handle both string and dict arguments
                arguments = tool_data.get_parsed_arguments()

                server_name = tool_data.server
                client = await self._get_or_create_client(server_name)
                if not client:
                    raise RuntimeError(f"Server '{server_name}' not available for tool '{tool_name}'")
                tool_result = await client.call_tool(tool_name, arguments)

                return ApiChatMessage(
                    role="tool",
                    content=json.dumps(tool_result),
                    tool_call_id=tool_data.id,
                    name=tool_name,
                )
            except Exception as e:
                error_message = f"Tool execution failed: {str(e)}"
                print(f"Error executing tool {tool_data.name}: {e}")
                return ApiChatMessage(
                    role="tool",
                    content=json.dumps({"error": error_message}),
                    tool_call_id=tool_data.id,
                    name=tool_data.name,
                )

        if not tool_execution_data:
            return []

        # Execute all tool calls in parallel
        tool_execution_tasks = [execute_single_tool(tool_data) for tool_data in tool_execution_data]

        tool_messages = await asyncio.gather(*tool_execution_tasks, return_exceptions=True)

        # Handle any exceptions that occurred during execution
        result_messages = []
        for tool_message in tool_messages:
            if isinstance(tool_message, Exception):
                print(f"Tool execution task failed: {tool_message}")
                # Create error message for failed task
                error_tool_message = ApiChatMessage(
                    role="tool",
                    content=json.dumps({"error": f"Task execution failed: {str(tool_message)}"}),
                    tool_call_id="error",
                    name="error",
                )
                result_messages.append(error_tool_message)
            else:
                result_messages.append(tool_message)

        return result_messages

    async def connect(self) -> Dict[str, bool]:
        """Connect to all MCP servers in parallel.

        Returns:
            Dictionary mapping server names to connection status
        """
        # Initialize clients if needed
        for server_name in self._server_config:
            if server_name not in self._mcp_clients:
                await self._get_or_create_client(server_name)

        # Connect to all servers in parallel
        tasks = []
        server_names = []

        for server_name, client in self._mcp_clients.items():
            if client:
                tasks.append(client.connect())
                server_names.append(server_name)

        # Execute connections in parallel
        results = {}
        if tasks:
            statuses = await asyncio.gather(*tasks, return_exceptions=True)

            for server_name, status in zip(server_names, statuses):
                if isinstance(status, Exception):
                    print(f"Failed to connect to {server_name}: {status}")
                    results[server_name] = False
                else:
                    results[server_name] = status

        return results

    async def disconnect(self):
        """Disconnect from all MCP servers."""
        for server_name, client in self._mcp_clients.items():
            try:
                client.disconnect()
            except Exception as e:
                print(f"Error disconnecting from {server_name}: {e}")

        self._mcp_clients.clear()

    async def test_connection(self) -> bool:
        """
        Test multi-MCP server connections.

        Returns:
            True if at least one MCP server is accessible
        """
        try:
            # Try to discover tools as a connectivity test
            tools = await self.discover_tools()
            return len(tools) > 0

        except Exception as e:
            print(f"Test connection failed: {e}")
            return False

    def get_server_config(self) -> Dict[str, Any]:
        """Get the current server configuration."""
        return self._server_config.copy()

    @property
    def server_mapping(self) -> Dict[str, str]:
        """Get server name to URL mapping for API responses."""
        return {server_name: config["url"] for server_name, config in self._server_config.items()}

    def get_enabled_servers(self) -> List[str]:
        """Get list of enabled server names."""
        return list(self._server_config.keys())

    async def get_server_health(self) -> Dict[str, bool]:
        """Get health status of all enabled servers."""
        health_status = {}

        for server_name in self._server_config:
            try:
                client = await self._get_or_create_client(server_name)
                health_status[server_name] = client is not None
            except Exception:
                health_status[server_name] = False

        return health_status

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Module-level singleton instance
mcp_client = _MCPClient()
singleton_manager.register(mcp_client)
