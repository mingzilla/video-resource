from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GenericToolCall(BaseModel):
    """Generic tool call structure that any LLM provider can populate."""

    id: str = Field(..., description="Tool call ID")
    type: str = Field(default="function", description="Type of tool call")
    function: Dict[str, Any] = Field(..., description="Function call details with name and arguments")

    def to_chat_message_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for ChatMessage storage."""
        return {
            "id": self.id,
            "type": self.type,
            "function": {
                "name": self.function["name"],
                "arguments": self.function["arguments"],
            },
        }

    @property
    def name(self) -> str:
        """Get tool name for generic access."""
        return self.function["name"]

    @property
    def arguments_str(self) -> str:
        """Get tool arguments as string for generic access."""
        return self.function["arguments"]


class LlmResponse(BaseModel):
    """Generic LLM response model that abstracts away provider-specific formats."""

    content: Optional[str] = Field(None, description="Response text content")
    tool_calls: Optional[List[GenericToolCall]] = Field(None, description="Tool calls made by LLM")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")

    def to_chat_message_dict(self) -> Optional[List[Dict[str, Any]]]:
        """
        Convert tool calls to ChatMessage dict format for conversation storage.

        Returns:
            List of tool call dictionaries or None if no tool calls
        """
        if not self.tool_calls:
            return None

        return [tc.to_chat_message_dict() for tc in self.tool_calls]

    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return bool(self.tool_calls)

    def get_tool_execution_data(self) -> List[Dict[str, Any]]:
        """
        Get tool execution data for MCP client calls.

        Returns:
            List of dicts with 'name' and 'arguments' keys for tool execution
        """
        if not self.tool_calls:
            return []

        return [{"id": tc.id, "name": tc.name, "arguments": tc.arguments_str} for tc in self.tool_calls]

    def get_status_text(self) -> str:
        """
        Get response content or generate status message for tool calls.

        Returns:
            Response content or tool status message
        """
        response_content = self.content or ""
        if self.has_tool_calls() and not response_content.strip():
            # If LLM only made tool calls without explanation, yield a status message
            tool_names = [tc.name for tc in self.tool_calls]
            response_content = f"Using tools: {', '.join(tool_names)}..."
        return response_content
