"""Internal business logic boundary models with Domain* prefix.

This module contains models representing business concepts and internal workflows:
- Core business concepts and entities
- Internal workflow and process models
- Models representing business rules and logic
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class DomainToolSelection(BaseModel):
    """Model for tool selection with server information."""

    name: str = Field(..., description="Tool name")
    server: Optional[str] = Field(None, description="Server name providing the tool")


class DomainToolExecutionRequest(BaseModel):
    """Model for tool execution request data."""

    name: str = Field(..., description="Tool name to execute")
    arguments: Union[str, Dict[str, Any]] = Field(..., description="Tool arguments (JSON string or dict)")
    id: str = Field(..., description="Tool call ID for tracking")
    server: Optional[str] = Field(None, description="Server name providing the tool")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainToolExecutionRequest":
        """Convert dict to ToolExecutionRequest for boundary model pattern.

        Args:
            data: Dictionary with 'name', 'arguments', and 'id' keys

        Returns:
            Typed DomainToolExecutionRequest object

        Raises:
            ValidationError: If conversion fails or required fields missing
        """
        return cls.model_validate(data)

    def get_parsed_arguments(self) -> Dict[str, Any]:
        """Parse arguments to dict format, handling both string and dict inputs."""
        if isinstance(self.arguments, str):
            import json

            return json.loads(self.arguments)
        return self.arguments


class DomainMcpTool(BaseModel):
    """Type-safe model for MCP tool definitions."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="Tool input schema")
    server: str = Field(..., description="Server name providing the tool")
    server_url: str = Field(..., description="Server URL")
    server_description: str = Field(..., description="Server description")

    @classmethod
    def from_dict(cls, data: Any, server: str, server_url: str, server_description: str = "") -> "DomainMcpTool":
        """Convert boundary model to domain model with server context.

        Args:
            data: McpToolDiscoveryItem object or dict with tool data
            server: Server name providing the tool
            server_url: Server URL
            server_description: Server description

        Returns:
            Typed DomainMcpTool object with server context

        Raises:
            ValidationError: If conversion fails, indicating API change
        """
        if hasattr(data, "name") and hasattr(data, "description") and hasattr(data, "inputSchema"):
            # Handle McpToolDiscoveryItem object
            return cls(
                name=data.name,
                description=data.description or "",
                input_schema=data.inputSchema or {},
                server=server,
                server_url=server_url,
                server_description=server_description,
            )
        elif isinstance(data, dict):
            # Handle dict format
            return cls(
                name=data["name"],
                description=data.get("description", ""),
                input_schema=data.get("input_schema", {}),
                server=server,
                server_url=server_url,
                server_description=server_description,
            )
        else:
            raise ValueError(f"Unexpected tool data format: {type(data)}")


class DomainHttpToolDiscoveryResponse(BaseModel):
    """Type-safe model for HTTP MCP server tool discovery response."""

    tools: List[Dict[str, Any]] = Field(..., description="List of tool definitions")
    count: Optional[int] = Field(None, description="Number of tools")
    mcp_servers: Optional[Dict[str, str]] = Field(None, description="Server mapping")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainHttpToolDiscoveryResponse":
        """Convert HTTP JSON response to typed model.

        Args:
            data: Raw JSON response from HTTP MCP server

        Returns:
            Typed DomainHttpToolDiscoveryResponse object

        Raises:
            ValidationError: If conversion fails, indicating API change
        """
        return cls.model_validate(data)


class DomainHttpToolExecutionResponse(BaseModel):
    """Type-safe model for HTTP MCP server tool execution response."""

    result: Optional[Any] = Field(None, description="Tool execution result")
    tool_name: Optional[str] = Field(None, description="Name of executed tool")
    arguments: Optional[Dict[str, Any]] = Field(None, description="Tool arguments used")
    error: Optional[str] = Field(None, description="Error message if failed")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainHttpToolExecutionResponse":
        """Convert HTTP JSON response to typed model.

        Args:
            data: Raw JSON response from HTTP tool execution

        Returns:
            Typed DomainHttpToolExecutionResponse object

        Raises:
            ValidationError: If conversion fails, indicating API change
        """
        return cls.model_validate(data)

    def get_result(self) -> Any:
        """Get the result data, handling both direct result and nested result patterns.

        Returns:
            Tool execution result data

        Raises:
            RuntimeError: If tool execution failed
        """
        if self.error:
            raise RuntimeError(f"Tool execution error: {self.error}")

        return self.result if self.result is not None else {}
