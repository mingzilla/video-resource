import asyncio
import os
from typing import Any, Dict, List, Optional

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPClient:
    """Multi-MCP client wrapper for communicating with multiple MCP servers."""

    def __init__(self):
        """Initialize MCP client with connections to multiple servers."""
        # Use Windows IP for WSL environment compatibility
        windows_ip = os.getenv("WINDOWS_IP")

        # Configure multiple MCP server URLs
        if windows_ip:
            server_mapping = {"api_config": f"http://{windows_ip}:8000/mcp/", "calculator": f"http://{windows_ip}:8010/mcp/"}
        else:
            # Fallback to localhost for non-WSL environments
            server_mapping = {"api_config": "http://127.0.0.1:8000/mcp/", "calculator": "http://127.0.0.1:8010/mcp/"}

        # Initialize multi-MCP client - for now, create a simple dual client approach
        self.server_mapping = server_mapping
        self.api_config_client = None
        self.calculator_client = None

        # Legacy compatibility properties
        self.server_url = server_mapping["api_config"]  # Backward compatibility
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        # Legacy MCP client session components (for backward compatibility)
        self._session: Optional[ClientSession] = None
        self._read_stream = None
        self._write_stream = None
        self._client_context = None

        # Cache for available tools
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        self._connected = False

    async def get_filtered_tools(self, selected_tools: Optional[List[str]]) -> List[Dict[str, Any]]:
        mcp_tools = await self.discover_tools()
        return [tool for tool in mcp_tools if tool["name"] in selected_tools]

    async def discover_tools(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Discover available tools from all MCP servers.

        Args:
            force_refresh: Force refresh of tools cache

        Returns:
            List of tool definitions from all servers
        """
        # Return cached tools if available and not forcing refresh
        if self._tools_cache and not force_refresh:
            return self._tools_cache

        all_tools = []

        # Discover tools from API config server
        try:
            if not self.api_config_client:
                self.api_config_client = await self._create_mcp_client("api_config")

            if self.api_config_client:
                api_tools = await self.api_config_client.discover_tools(force_refresh)
                for tool in api_tools:
                    tool["_server"] = "api_config"
                    tool["_server_url"] = self.server_mapping["api_config"]
                all_tools.extend(api_tools)
                print(f"Found {len(api_tools)} API config tools")
        except Exception as e:
            print(f"Error discovering API config tools: {e}")

        # Discover tools from calculator server
        try:
            if not self.calculator_client:
                self.calculator_client = await self._create_mcp_client("calculator")

            if self.calculator_client:
                calc_tools = await self.calculator_client.discover_tools(force_refresh)
                for tool in calc_tools:
                    tool["_server"] = "calculator"
                    tool["_server_url"] = self.server_mapping["calculator"]
                all_tools.extend(calc_tools)
                print(f"Found {len(calc_tools)} calculator tools")
        except Exception as e:
            print(f"Error discovering calculator tools: {e}")

        # Cache the tools
        self._tools_cache = all_tools
        self._connected = len(all_tools) > 0

        return all_tools

    async def _create_mcp_client(self, server_name: str):
        """Create an individual MCP client for a specific server."""
        try:
            # Create a simple MCPClient that connects to a specific server

            # Create a temporary class to override the server URL
            class SingleServerMCPClient:
                def __init__(self, server_url):
                    self.server_url = server_url
                    self.headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                    }
                    self._session = None
                    self._read_stream = None
                    self._write_stream = None
                    self._client_context = None
                    self._tools_cache = None
                    self._connected = False

                async def discover_tools(self, force_refresh: bool = False):
                    if not self._connected:
                        if not await self.connect():
                            return []

                    if self._tools_cache and not force_refresh:
                        return self._tools_cache

                    try:
                        if not self._session:
                            return []

                        tools_response = await self._session.list_tools()
                        tools = []
                        for tool in tools_response.tools:
                            tool_def = {
                                "name": tool.name,
                                "description": tool.description or "",
                                "input_schema": tool.inputSchema or {},
                            }
                            tools.append(tool_def)

                        self._tools_cache = tools
                        return tools

                    except Exception as e:
                        print(f"Error discovering tools from {server_name}: {e}")
                        return []

                async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
                    if not self._connected:
                        if not await self.connect():
                            raise RuntimeError("Failed to connect to MCP server")

                    try:
                        if not self._session:
                            raise RuntimeError("MCP session not initialized")

                        result = await self._session.call_tool(tool_name, arguments)

                        if result and result.content:
                            content = result.content[0]
                            if content.type == "text":
                                try:
                                    import json

                                    parsed_data = json.loads(content.text)
                                    return parsed_data
                                except json.JSONDecodeError:
                                    text_content = content.text
                                    if "Error executing tool" in text_content:
                                        raise RuntimeError(f"MCP Tool Error: {text_content}")
                                    return {"text": text_content}

                        return {}

                    except Exception as e:
                        raise RuntimeError(f"Tool call failed: {str(e)}")

                async def connect(self):
                    try:
                        if self._connected:
                            await self.disconnect()

                        import asyncio

                        async with asyncio.timeout(5.0):
                            client_context = streamablehttp_client(self.server_url, self.headers)
                            self._client_context = client_context
                            streams = await client_context.__aenter__()
                            self._read_stream, self._write_stream, _ = streams

                            self._session = ClientSession(self._read_stream, self._write_stream)
                            await self._session.__aenter__()
                            await self._session.initialize()

                            self._connected = True
                            return True

                    except Exception as e:
                        print(f"Failed to connect to {server_name} at {self.server_url}: {e}")
                        await self.disconnect()
                        return False

                async def disconnect(self):
                    try:
                        self._connected = False
                        if self._session:
                            try:
                                await self._session.__aexit__(None, None, None)
                            except Exception:
                                pass
                            finally:
                                self._session = None

                        if self._client_context:
                            try:
                                await self._client_context.__aexit__(None, None, None)
                            except Exception:
                                pass
                            finally:
                                self._client_context = None

                        self._read_stream = None
                        self._write_stream = None
                        self._tools_cache = None

                    except Exception as e:
                        print(f"Error during disconnect from {server_name}: {e}")

            # Create client for the specified server
            server_url = self.server_mapping[server_name]
            client = SingleServerMCPClient(server_url)

            if await client.connect():
                return client
            else:
                return None

        except Exception as e:
            print(f"Failed to create MCP client for {server_name}: {e}")
            return None

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the appropriate MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            # Route tool call to appropriate server
            if tool_name in ["add", "multiply"]:
                # Calculator tools go to calculator server
                if not self.calculator_client:
                    self.calculator_client = await self._create_mcp_client("calculator")
                if self.calculator_client:
                    return await self.calculator_client.call_tool(tool_name, arguments)
                else:
                    raise RuntimeError("Calculator server not available")
            else:
                # API config tools go to API config server
                if not self.api_config_client:
                    self.api_config_client = await self._create_mcp_client("api_config")
                if self.api_config_client:
                    return await self.api_config_client.call_tool(tool_name, arguments)
                else:
                    raise RuntimeError("API config server not available")

        except Exception as e:
            raise RuntimeError(f"Tool call failed: {str(e)}")

    async def connect(self) -> bool:
        """
        Establish connection to MCP server using official MCP client.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Close any existing connection first
            if self._connected:
                await self.disconnect()

            # Connect to streamable HTTP server with proper context management
            async with asyncio.timeout(5.0):
                # Create the client context
                client_context = streamablehttp_client(self.server_url, self.headers)

                # Store the context manager but don't exit it - let it live for the lifetime
                self._client_context = client_context

                # Enter the context and get streams
                streams = await client_context.__aenter__()
                self._read_stream, self._write_stream, _ = streams

                # Create session and initialize
                self._session = ClientSession(self._read_stream, self._write_stream)
                await self._session.__aenter__()
                await self._session.initialize()

                self._connected = True
                return True

        except asyncio.TimeoutError:
            print(f"Timeout connecting to MCP server at {self.server_url}")
            await self.disconnect()
            return False
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            await self.disconnect()
            return False

    async def disconnect(self):
        """Disconnect from all MCP servers."""
        try:
            self._connected = False

            # Cleanup individual MCP clients
            if self.api_config_client:
                await self.api_config_client.disconnect()
                self.api_config_client = None

            if self.calculator_client:
                await self.calculator_client.disconnect()
                self.calculator_client = None

            # Legacy cleanup for backward compatibility
            if self._session:
                try:
                    await self._session.__aexit__(None, None, None)
                except Exception as e:
                    print(f"Warning: Error closing MCP session: {e}")
                finally:
                    self._session = None

            if self._client_context:
                try:
                    await self._client_context.__aexit__(None, None, None)
                except Exception as e:
                    print(f"Warning: Error closing MCP client context: {e}")
                finally:
                    self._client_context = None

            # Clear stream references
            self._read_stream = None
            self._write_stream = None

            # Clear tools cache on disconnect
            self._tools_cache = None

        except Exception as e:
            print(f"Error during disconnect: {e}")
            # Ensure cleanup even if errors occur
            self._session = None
            self._client_context = None
            self._read_stream = None
            self._write_stream = None
            self._tools_cache = None

    async def is_connected(self) -> bool:
        """Check if connected to MCP server."""
        return self._connected and self._session is not None

    async def test_connection(self) -> bool:
        """
        Test multi-MCP server connections.

        Returns:
            True if at least one MCP server is accessible
        """
        try:
            # Try to discover tools as a connectivity test
            tools = await self.discover_tools(force_refresh=True)
            success = len(tools) > 0
            if success:
                self._connected = True
            return success

        except Exception as e:
            print(f"Test connection failed: {e}")
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
