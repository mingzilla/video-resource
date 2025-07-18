from typing import Any, Dict, List

from github_mingzilla.llm_mcp.models import ApiChatMessage, DomainMcpTool, LlmResponse, LlmToolCall, OpenAIMessage


class LlmOpenaiUtil:
    @staticmethod
    def mcp_to_openai_function(mcp_tool: DomainMcpTool) -> Dict[str, Any]:
        """
        Convert MCP tool schema to OpenAI function schema.

        Args:
            mcp_tool: DomainMcpTool object

        Returns:
            OpenAI function schema
        """
        function_def = {
            "type": "function",
            "function": {
                "name": mcp_tool.name,
                "description": mcp_tool.description,
            },
        }

        # Convert input schema to OpenAI parameters format
        input_schema = mcp_tool.input_schema
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
    def mcp_to_openai_functions(mcp_tools: List[DomainMcpTool]) -> List[Dict[str, Any]]:
        """
        Get available tools in OpenAI function format.

        Args:
            mcp_tools: List of DomainMcpTool objects

        Returns:
            List of OpenAI function definitions
        """
        return [LlmOpenaiUtil.mcp_to_openai_function(tool) for tool in mcp_tools]

    @staticmethod
    def chat_messages_to_openai_format(messages: List[ApiChatMessage]) -> List[Dict[str, Any]]:
        """
        Convert ApiChatMessage objects to OpenAI API format.

        Args:
            messages: List of ApiChatMessage objects

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
    def openai_response_to_llm_response(openai_message: OpenAIMessage, model: str = None, provider: str = None) -> LlmResponse:
        """
        Convert typed OpenAI message to generic LlmResponse.

        Args:
            openai_message: Typed OpenAIMessage object
            model: Model name used for the request
            provider: Provider name used for the request

        Returns:
            Generic LlmResponse object
        """
        # Extract content from typed message
        content = openai_message.content

        # Convert tool calls if present
        tool_calls = None
        if openai_message.tool_calls:
            tool_calls = []
            for tc in openai_message.tool_calls:
                generic_tc = LlmToolCall(
                    id=tc.id,
                    type=tc.type,
                    function=tc.function,
                )
                tool_calls.append(generic_tc)

        return LlmResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=None,  # Not available in message object
            model=model,
            provider=provider,
            usage=None,  # Can be added later if needed
        )
