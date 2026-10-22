"""OpenAI API boundary models with OpenAI* prefix.

This module contains boundary models for external OpenAI API:
- OpenAI API response models with from_dict() conversion
- Type-safe boundaries for OpenAI integrations
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OpenAIToolCall(BaseModel):
    """Type-safe model for OpenAI tool call structure."""

    id: str = Field(..., description="Tool call ID")
    type: str = Field(..., description="Tool call type")
    function: Dict[str, Any] = Field(..., description="Function call details")

    @classmethod
    def from_dict(cls, data: Any) -> "OpenAIToolCall":
        """Convert OpenAI tool call object to typed model.

        Args:
            data: Raw tool call object from OpenAI API

        Returns:
            Typed OpenAIToolCall object

        Raises:
            ValidationError: If conversion fails, indicating OpenAI API change
        """
        if hasattr(data, "id"):
            # Convert object with attributes
            return cls(
                id=data.id,
                type=data.type,
                function={
                    "name": data.function.name,
                    "arguments": data.function.arguments,
                },
            )
        elif isinstance(data, dict):
            return cls.model_validate(data)
        else:
            raise ValueError(f"Unexpected OpenAI tool call format: {type(data)}")


class OpenAIMessage(BaseModel):
    """Type-safe model for OpenAI message response."""

    content: Optional[str] = Field(None, description="Message content")
    tool_calls: Optional[List[OpenAIToolCall]] = Field(None, description="Tool calls in message")

    @classmethod
    def from_dict(cls, data: Any) -> "OpenAIMessage":
        """Convert OpenAI message object to typed model.

        Args:
            data: Raw message object from OpenAI API

        Returns:
            Typed OpenAIMessage object

        Raises:
            ValidationError: If conversion fails, indicating OpenAI API change
            AttributeError: If object is missing expected attributes
        """
        if isinstance(data, dict):
            return cls.model_validate(data)
        else:
            # Try to access attributes - differentiate between object missing attributes vs invalid types
            try:
                # Check if this looks like an object that should have attributes
                if hasattr(data, "__dict__") or hasattr(data, "__slots__"):
                    # This is an object - let AttributeError propagate for missing attributes
                    content = data.content
                    tool_calls = None
                    if hasattr(data, "tool_calls") and data.tool_calls:
                        tool_calls = [OpenAIToolCall.from_dict(tc) for tc in data.tool_calls]
                    return cls(content=content, tool_calls=tool_calls)
                else:
                    # This is not an object type - raise ValueError
                    raise ValueError(f"Unexpected OpenAI message format: {type(data)}")
            except AttributeError:
                # Re-raise AttributeError for missing attributes on actual objects
                raise
            except Exception:
                raise ValueError(f"Unexpected OpenAI message format: {type(data)}")
