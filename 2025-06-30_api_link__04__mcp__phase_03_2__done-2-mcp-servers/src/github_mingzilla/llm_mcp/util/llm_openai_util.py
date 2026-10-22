from typing import Any, Dict, List

from github_mingzilla.llm_mcp.models.chat_models import ChatMessage
from github_mingzilla.llm_mcp.models.llm_models import GenericToolCall, LlmResponse


class LlmOpenaiUtil:
    @staticmethod
    def mcp_to_openai_function(mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
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
                "description": mcp_tool["description"],
            },
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
                "required": [],
            }

        return function_def

    @staticmethod
    def mcp_to_openai_functions(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get available tools in OpenAI function format.

        Returns:
            List of OpenAI function definitions
        """
        return [LlmOpenaiUtil.mcp_to_openai_function(tool) for tool in mcp_tools]

    @staticmethod
    def chat_messages_to_openai_format(messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """
        Convert ChatMessage objects to OpenAI API format.

        Args:
            messages: List of ChatMessage objects

        Returns:
            List of OpenAI-formatted message dictionaries
        """
        openai_messages = []
        for msg in messages:
            openai_msg = {"role": msg.role}

            # Add content if present
            if msg.content is not None:
                openai_msg["content"] = msg.content

            # Add tool calls for assistant messages (already in OpenAI format from storage)
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls

            # Add tool call info for tool messages
            if msg.role == "tool":
                openai_msg["tool_call_id"] = msg.tool_call_id
                if msg.name:
                    openai_msg["name"] = msg.name

            openai_messages.append(openai_msg)

        return openai_messages

    @staticmethod
    def openai_response_to_llm_response(openai_message) -> LlmResponse:
        """
        Convert OpenAI API response message to generic LlmResponse.

        Args:
            openai_message: OpenAI message object from API response

        Returns:
            Generic LlmResponse object
        """
        # Extract content
        content = openai_message.content

        # Convert tool calls if present
        tool_calls = None
        if openai_message.tool_calls:
            tool_calls = []
            for tc in openai_message.tool_calls:
                generic_tc = GenericToolCall(
                    id=tc.id,
                    type=tc.type,
                    function={
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                )
                tool_calls.append(generic_tc)

        return LlmResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=None,  # Not available in message object
            usage=None,  # Can be added later if needed
        )
