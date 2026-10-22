"""HTTP API boundary models with Api* prefix.

This module contains models that cross HTTP API boundaries:
- Request/response models for our REST endpoints
- Data transfer objects for API communication
- Models that external clients see
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from github_mingzilla.llm_mcp.boundary_models.domain_boundary_models import DomainToolSelection


class ApiChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., description="User message to send to LLM")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")
    model: Optional[str] = Field(default="gpt-4.1-nano", description="LLM model to use")
    selected_tools: Optional[List[DomainToolSelection]] = Field(None, description="List of tool selection objects with server info")


class ApiChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="LLM response content")
    session_id: str = Field(..., description="Session ID for this conversation")
    model: str = Field(..., description="LLM model used")
    usage: Optional[dict] = Field(None, description="Token usage information")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls made during response")


class ApiChatMessage(BaseModel):
    """Individual chat message model."""

    role: str = Field(..., description="Message role: 'user', 'assistant', 'system', or 'tool'")
    content: Optional[str] = Field(None, description="Message content")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls made by assistant")
    tool_call_id: Optional[str] = Field(None, description="ID of tool call (for tool role messages)")
    name: Optional[str] = Field(None, description="Name of tool that was called (for tool role messages)")


class ApiToolCall(BaseModel):
    """Model for tool call information."""

    id: str = Field(..., description="Tool call ID")
    type: str = Field(default="function", description="Type of tool call")
    function: Dict[str, Any] = Field(..., description="Function call details")
