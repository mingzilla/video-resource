import asyncio
from typing import Any, Dict, List, Optional

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from github_mingzilla.llm_mcp.boundary_models import McpToolDiscoveryItem, McpToolResponse, McpToolsListResponse


class SingleServerMCPClient:
    def __init__(self, server_name: str, server_url: str):
        self.server_name = server_name
        self.server_url = server_url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        self.tools: Optional[List[McpToolDiscoveryItem]] = None

    async def discover_tools(self) -> List[McpToolDiscoveryItem]:
        """Discover tools with simple caching - return cached OR fetch->cache->return."""
        if self.tools is not None:
            return self.tools

        try:
            # Create temporary session for tool discovery
            async with asyncio.timeout(5.0):
                client_context = streamablehttp_client(self.server_url, self.headers)
                streams = await client_context.__aenter__()
                read_stream, write_stream, _ = streams

                session = ClientSession(read_stream, write_stream)
                await session.__aenter__()
                await session.initialize()

                # External library boundary - get raw response
                raw_tools_response = await session.list_tools()

                # Convert to typed model at boundary
                typed_response = McpToolsListResponse.from_dict(raw_tools_response)

                # Cache and return typed tools
                self.tools = typed_response.tools

                # Cleanup temporary session
                await session.__aexit__(None, None, None)
                await client_context.__aexit__(None, None, None)

                return self.tools

        except Exception as e:
            print(f"Error discovering tools from {self.server_url}: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Execute tool call with temporary session."""
        try:
            # Create temporary session for tool execution
            async with asyncio.timeout(10.0):
                client_context = streamablehttp_client(self.server_url, self.headers)
                streams = await client_context.__aenter__()
                read_stream, write_stream, _ = streams

                session = ClientSession(read_stream, write_stream)
                await session.__aenter__()
                await session.initialize()

                # External library boundary - get raw response
                raw_result = await session.call_tool(tool_name, arguments)

                # Cleanup temporary session
                await session.__aexit__(None, None, None)
                await client_context.__aexit__(None, None, None)

                if raw_result and raw_result.content:
                    # Convert to typed model at boundary
                    typed_result = McpToolResponse.from_dict(raw_result)
                    return typed_result.parse_content()

                return {}

        except Exception as e:
            raise RuntimeError(f"Tool call failed: {str(e)}")

    async def connect(self) -> bool:
        """Simple connect - just call discover_tools() and return success."""
        tools = await self.discover_tools()
        return len(tools) > 0

    def disconnect(self):
        """Simple disconnect - clear the tools cache."""
        self.tools = None
