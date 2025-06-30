# Standard Library
import asyncio
import json
import os
from typing import Any, Dict, List, Optional

# Third Party
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MCPClient:
    """MCP client wrapper for communicating with Server 2 (MCP Proxy)."""

    def __init__(self):
        """Initialize MCP client with connection to Server 2."""
        self.server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp/")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        # Cache for available tools
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._connected = False

    async def connect(self) -> bool:
        """
        Establish connection to MCP server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create HTTP client if not exists
            if not hasattr(self, '_http_client') or self._http_client is None:
                self._http_client = httpx.AsyncClient(
                    timeout=10.0,
                    headers=self.headers
                )

            # Test connection with a simple request
            async with asyncio.timeout(5.0):
                # Try to list tools to test connection
                response = await self._make_http_request("tools/list", {})
                if response:
                    self._connected = True
                    return True

            return False

        except asyncio.TimeoutError:
            print(f"Timeout connecting to MCP server at {self.server_url}")
            self._connected = False
            return False
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            self._connected = False
            return False

    async def disconnect(self):
        """Disconnect from MCP server."""
        try:
            self._connected = False

            # Close HTTP client
            if hasattr(self, '_http_client') and self._http_client:
                try:
                    await self._http_client.aclose()
                except Exception:
                    pass  # Ignore errors during cleanup
                self._http_client = None

        except Exception as e:
            print(f"Error during disconnect: {e}")

    async def is_connected(self) -> bool:
        """Check if connected to MCP server."""
        return self._connected and self._session is not None

    async def discover_tools(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Discover available tools from MCP server.

        Args:
            force_refresh: Force refresh of tools cache

        Returns:
            List of tool definitions
        """
        if not self._connected:
            if not await self.connect():
                return []

        # Return cached tools if available and not forcing refresh
        if self._tools_cache and not force_refresh:
            return self._tools_cache

        try:
            # List available tools from MCP server using direct HTTP
            response = await self._make_http_request("tools/list", {})

            # Convert MCP tool format to our internal format
            tools = []
            if response and "result" in response and "tools" in response["result"]:
                for tool in response["result"]["tools"]:
                    tool_def = {
                        "name": tool.get("name", ""),
                        "description": tool.get("description", ""),
                        "input_schema": tool.get("inputSchema", {})
                    }
                    tools.append(tool_def)

            # Cache the tools
            self._tools_cache = tools
            return tools

        except Exception as e:
            print(f"Error discovering tools: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if not self._connected:
            if not await self.connect():
                raise RuntimeError("Failed to connect to MCP server")

        try:
            # Execute the tool call using direct HTTP
            response = await self._make_http_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })

            if not response or "result" not in response:
                raise RuntimeError(f"Invalid response from MCP server: {response}")

            tool_result = response["result"]

            # Handle MCP tool response structure like in working test
            if "content" in tool_result and tool_result["content"]:
                content = tool_result["content"][0]
                if content.get("type") == "text":
                    # Parse JSON string from text content
                    try:
                        parsed_data = json.loads(content["text"])
                        return parsed_data
                    except json.JSONDecodeError:
                        # If not JSON, return the text as-is
                        text_content = content["text"]
                        # Check if this is an error message
                        if "Error executing tool" in text_content:
                            raise RuntimeError(f"MCP Tool Error: {text_content}")
                        return {"text": text_content}

            # Return the raw result if no content structure
            return tool_result

        except Exception as e:
            raise RuntimeError(f"Tool call failed: {str(e)}")

    def mcp_to_openai_function(self, mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MCP tool schema to OpenAI function schema.

        Args:
            mcp_tool: MCP tool definition

        Returns:
            OpenAI function schema
        """
        function_def = {
            "type": "function",
            "function": {
                "name": mcp_tool["name"],
                "description": mcp_tool["description"]
            }
        }

        # Convert input schema to OpenAI parameters format
        input_schema = mcp_tool.get("input_schema", {})
        if input_schema:
            # MCP uses JSON Schema, which is compatible with OpenAI
            function_def["function"]["parameters"] = input_schema
        else:
            # Default empty parameters
            function_def["function"]["parameters"] = {
                "type": "object",
                "properties": {},
                "required": []
            }

        return function_def

    async def get_openai_functions(self) -> List[Dict[str, Any]]:
        """
        Get available tools in OpenAI function format.

        Returns:
            List of OpenAI function definitions
        """
        mcp_tools = await self.discover_tools()
        return [self.mcp_to_openai_function(tool) for tool in mcp_tools]

    async def test_connection(self) -> bool:
        """
        Test MCP server connection.

        Returns:
            True if connection and basic operations work
        """
        try:
            # Quick connection test with timeout
            async with asyncio.timeout(10.0):  # 10 second total timeout
                if not await self.connect():
                    return False

                # Try to discover tools as a connectivity test
                tools = await self.discover_tools()
                return len(tools) >= 0  # Even empty list is valid

        except asyncio.TimeoutError:
            print(f"Test connection timeout to {self.server_url}")
            return False
        except Exception as e:
            print(f"Test connection failed: {e}")
            return False
        finally:
            # Don't disconnect for test - leave connection open for subsequent use
            pass

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def _make_http_request(self, method: str, params: Dict[str, Any], call_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to MCP server using the same pattern as working test.

        Args:
            method: MCP method name
            params: Method parameters
            call_id: JSON-RPC call ID

        Returns:
            Parsed response or None on error
        """
        if not self._http_client:
            return None

        payload = {
            "jsonrpc": "2.0",
            "id": call_id,
            "method": method,
            "params": params
        }

        try:
            print(f"Making MCP request to {self.server_url}")
            print(f"Payload: {payload}")
            print(f"Headers: {self.headers}")

            response = await self._http_client.post(
                self.server_url,
                json=payload,
                headers=self.headers
            )

            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text[:500]}...")

            response.raise_for_status()

            # Parse SSE response like in working test
            return self._parse_sse_response(response.text)

        except Exception as e:
            print(f"HTTP request failed: {e}")
            print(f"Exception type: {type(e)}")
            return None

    def _parse_sse_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse Server-Sent Events response format.

        Args:
            response_text: Raw response text

        Returns:
            Parsed JSON data or None
        """
        try:
            for line in response_text.strip().split("\n"):
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if "error" in data:
                        raise RuntimeError(f"MCP Error: {data['error']}")
                    return data

            raise RuntimeError("No SSE data found in response")

        except json.JSONDecodeError as e:
            print(f"Failed to parse SSE response: {e}")
            return None
