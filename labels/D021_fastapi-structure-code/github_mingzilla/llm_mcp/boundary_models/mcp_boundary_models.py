"""MCP boundary models for Server 1 - MCP library protocol boundaries.

This module contains boundary models for MCP (Model Context Protocol) library:
- MCP tool execution response models with from_dict() conversion
- MCP tool discovery models with from_dict() conversion
- Type-safe boundaries for MCP library integration
"""

import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

# MCP Library Boundary Models


class McpToolContent(BaseModel):
    """Type-safe model for MCP tool response content item."""

    type: str = Field(..., description="Content type (usually 'text')")
    text: str = Field(..., description="Content text data")

    @classmethod
    def from_dict(cls, data: Any) -> "McpToolContent":
        """Convert MCP library content object to typed model.

        Args:
            data: Raw content object from MCP library (has .type and .text attributes)

        Returns:
            Typed McpToolContent object

        Raises:
            ValidationError: If conversion fails, indicating MCP library API change
            AttributeError: If object is missing expected attributes
        """
        if isinstance(data, dict):
            # Handle dict format
            return cls.model_validate(data)
        else:
            # Try to access attributes - differentiate between object missing attributes vs invalid types
            try:
                # Check if this looks like an object that should have attributes
                if hasattr(data, "__dict__") or hasattr(data, "__slots__"):
                    # This is an object - let AttributeError propagate for missing attributes
                    return cls(type=data.type, text=data.text)
                else:
                    # This is not an object type - raise ValueError
                    raise ValueError(f"Unexpected MCP content format: {type(data)}")
            except AttributeError:
                # Re-raise AttributeError for missing attributes on actual objects
                raise
            except Exception:
                raise ValueError(f"Unexpected MCP content format: {type(data)}")


class McpToolResponse(BaseModel):
    """Type-safe model for MCP tool execution response."""

    content: List[McpToolContent] = Field(..., description="List of content items from tool execution")

    @classmethod
    def from_dict(cls, data: Any) -> "McpToolResponse":
        """Convert MCP library tool response to typed model.

        Args:
            data: Raw response object from MCP library (has .content attribute)

        Returns:
            Typed McpToolResponse object

        Raises:
            ValidationError: If conversion fails, indicating MCP library API change
        """
        if hasattr(data, "content"):
            # Convert object with .content attribute
            content_items = [McpToolContent.from_dict(item) for item in data.content]
            return cls(content=content_items)
        elif isinstance(data, dict) and "content" in data:
            # Handle dict format
            return cls.model_validate(data)
        else:
            raise ValueError(f"Unexpected MCP tool response format: {type(data)}")

    def parse_content(self) -> Union[str, Dict[str, Any], List[Any]]:
        """Parse content items into structured data.

        Returns:
            Parsed data from content items, handling both single and multiple items

        Raises:
            RuntimeError: If tool execution error is detected
        """
        if len(self.content) == 0:
            return []
        elif len(self.content) == 1:
            content = self.content[0]
            if content.type == "text":
                try:
                    return json.loads(content.text)
                except json.JSONDecodeError:
                    if "Error executing tool" in content.text:
                        raise RuntimeError(f"MCP Tool Error: {content.text}")
                    return content.text
        else:
            # Multiple content items - combine them
            combined_data = []
            for content in self.content:
                if content.type == "text":
                    try:
                        parsed_data = json.loads(content.text)
                        combined_data.append(parsed_data)
                    except json.JSONDecodeError:
                        combined_data.append(content.text)
            return combined_data


class McpToolDiscoveryItem(BaseModel):
    """Type-safe model for individual MCP tool discovery item."""

    name: str = Field(..., description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    inputSchema: Optional[Dict[str, Any]] = Field(None, description="Tool input schema")

    @classmethod
    def from_dict(cls, data: Any) -> "McpToolDiscoveryItem":
        """Convert MCP library tool object to typed model.

        Args:
            data: Raw tool object from MCP library (has .name, .description, .inputSchema attributes)

        Returns:
            Typed McpToolDiscoveryItem object

        Raises:
            ValidationError: If conversion fails, indicating MCP library API change
            AttributeError: If object is missing expected attributes
        """
        if isinstance(data, dict):
            # Handle dict format
            return cls.model_validate(data)
        else:
            # Try to access attributes - differentiate between object missing attributes vs invalid types
            try:
                # Check if this looks like an object that should have attributes
                if hasattr(data, "__dict__") or hasattr(data, "__slots__"):
                    # This is an object - let AttributeError propagate for missing attributes
                    return cls(name=data.name, description=getattr(data, "description", None), inputSchema=getattr(data, "inputSchema", None))
                else:
                    # This is not an object type - raise ValueError
                    raise ValueError(f"Unexpected MCP tool discovery format: {type(data)}")
            except AttributeError:
                # Re-raise AttributeError for missing attributes on actual objects
                raise
            except Exception:
                raise ValueError(f"Unexpected MCP tool discovery format: {type(data)}")


class McpToolsListResponse(BaseModel):
    """Type-safe model for MCP tools list response."""

    tools: List[McpToolDiscoveryItem] = Field(..., description="List of discovered tools")

    @classmethod
    def from_dict(cls, data: Any) -> "McpToolsListResponse":
        """Convert MCP library tools list response to typed model.

        Args:
            data: Raw response object from MCP library (has .tools attribute)

        Returns:
            Typed McpToolsListResponse object

        Raises:
            ValidationError: If conversion fails, indicating MCP library API change
        """
        if hasattr(data, "tools"):
            # Convert object with .tools attribute
            tools_items = [McpToolDiscoveryItem.from_dict(tool) for tool in data.tools]
            return cls(tools=tools_items)
        elif isinstance(data, dict) and "tools" in data:
            # Handle dict format
            return cls.model_validate(data)
        else:
            raise ValueError(f"Unexpected MCP tools list format: {type(data)}")
