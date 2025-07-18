"""Server 1 models module - DEPRECATED: Use github_mingzilla.llm_mcp.boundary_models instead.

This module provides backward compatibility exports from the new boundary_models package.
Models have been moved to github_mingzilla.llm_mcp.boundary_models with consistent file naming.

For new code, import directly from: github_mingzilla.llm_mcp.boundary_models
"""

# Re-export all models from the new boundary_models package for backward compatibility
from github_mingzilla.llm_mcp.boundary_models import (
    ApiChatMessage,
    ApiChatRequest,
    ApiChatResponse,
    ApiToolCall,
    DomainHttpToolDiscoveryResponse,
    DomainHttpToolExecutionResponse,
    DomainMcpTool,
    DomainToolExecutionRequest,
    DomainToolSelection,
    LlmResponse,
    LlmToolCall,
    McpToolContent,
    McpToolDiscoveryItem,
    McpToolResponse,
    McpToolsListResponse,
    OllamaModel,
    OllamaModelsResponse,
    OpenAIMessage,
    OpenAIToolCall,
)

# Legacy aliases for backward compatibility
HttpToolDiscoveryResponse = DomainHttpToolDiscoveryResponse
HttpToolExecutionResponse = DomainHttpToolExecutionResponse

# Backward compatibility - all models available at package level
__all__ = [
    # API boundary models (Api* prefix)
    "ApiChatMessage",
    "ApiChatRequest",
    "ApiChatResponse",
    "ApiToolCall",
    # Domain boundary models (Domain* prefix)
    "DomainHttpToolDiscoveryResponse",
    "DomainHttpToolExecutionResponse",
    "DomainMcpTool",
    "DomainToolExecutionRequest",
    "DomainToolSelection",
    # LLM boundary models (Llm* prefix)
    "LlmResponse",
    "LlmToolCall",
    # MCP boundary models (Mcp* prefix)
    "McpToolContent",
    "McpToolDiscoveryItem",
    "McpToolResponse",
    "McpToolsListResponse",
    # Ollama boundary models (Ollama* prefix)
    "OllamaModel",
    "OllamaModelsResponse",
    # OpenAI boundary models (OpenAI* prefix)
    "OpenAIMessage",
    "OpenAIToolCall",
    # Legacy aliases for backward compatibility
    "HttpToolDiscoveryResponse",
    "HttpToolExecutionResponse",
]
