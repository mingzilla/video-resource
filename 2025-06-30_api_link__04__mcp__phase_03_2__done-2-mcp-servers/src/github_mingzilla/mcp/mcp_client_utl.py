import json
import os
from typing import Any, Dict

import requests


class McpClientUtil:
    # Use Windows IP for WSL environment compatibility
    @classmethod
    def _get_mcp_server_url(cls) -> str:
        windows_ip = os.getenv("WINDOWS_IP")
        if windows_ip:
            return f"http://{windows_ip}:8000/mcp"
        else:
            # Fallback to localhost for non-WSL environments
            return "http://127.0.0.1:8000/mcp"

    MCP_SERVER_URL = _get_mcp_server_url()
    TEST_CONFIG_NAME = "test_crud_api_config_mcp"
    HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

    @staticmethod
    def make_mcp_resource_call(uri: str, call_id: int = 1) -> str:
        """Helper method to make MCP resource calls."""
        payload = {"jsonrpc": "2.0", "id": call_id, "method": "resources/read", "params": {"uri": uri}}

        response = requests.post(McpClientUtil.MCP_SERVER_URL, json=payload, headers=McpClientUtil.HEADERS)
        response.raise_for_status()

        result = McpClientUtil.parse_response(response)
        contents = result.get("result", {}).get("contents", [])
        if contents:
            return contents[0].get("text", "")
        return ""

    @staticmethod
    def make_mcp_call(method: str, arguments: Dict[str, Any], call_id: int = 1) -> Dict[str, Any]:
        """Helper method to make MCP JSON-RPC tool calls."""
        payload = {"jsonrpc": "2.0", "id": call_id, "method": "tools/call", "params": {"name": method, "arguments": arguments}}

        response = requests.post(McpClientUtil.MCP_SERVER_URL, json=payload, headers=McpClientUtil.HEADERS)
        response.raise_for_status()

        result = McpClientUtil.parse_response(response)
        tool_result = result.get("result", {})

        # Handle MCP tool response structure
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

    @staticmethod
    def parse_response(response: requests.Response):
        result = None
        try:
            for line in response.text.strip().split("\n"):
                if line.startswith("data: "):
                    result = json.loads(line[6:])
                    return result
            raise RuntimeError("No SSE data found")
        finally:
            if result and "error" in result:
                raise RuntimeError(f"MCP Resource Error: {result['error']}")
