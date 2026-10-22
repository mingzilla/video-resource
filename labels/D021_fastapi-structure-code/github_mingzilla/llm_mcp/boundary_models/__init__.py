"""Boundary models package with consistent file naming convention.

This package organizes boundary models by domain with file naming pattern: {prefix}_boundary_models.py
- api_boundary_models.py: Api* prefix models (HTTP APIs)
- domain_boundary_models.py: Domain* prefix models (internal business)
- llm_boundary_models.py: Llm* prefix models (provider abstractions)
- openai_boundary_models.py: OpenAI* prefix models (OpenAI-specific)
- ollama_boundary_models.py: Ollama* prefix models (Ollama-specific)
- mcp_boundary_models.py: Mcp* prefix models (MCP-specific)
"""

# API boundary models exports (Http API request/response models)
from github_mingzilla.llm_mcp.boundary_models.api_boundary_models import (
    ApiChatMessage,
    ApiChatRequest,
    ApiChatResponse,
    ApiToolCall,
)

# Domain boundary models exports (Internal business logic models)
from github_mingzilla.llm_mcp.boundary_models.domain_boundary_models import (
    DomainHttpToolDiscoveryResponse,
    DomainHttpToolExecutionResponse,
    DomainMcpTool,
    DomainToolExecutionRequest,
    DomainToolSelection,
)

# LLM boundary models exports (LLM provider abstraction models)
from github_mingzilla.llm_mcp.boundary_models.llm_boundary_models import (
    LlmResponse,
    LlmToolCall,
)

# MCP boundary models exports (MCP library boundary models)
from github_mingzilla.llm_mcp.boundary_models.mcp_boundary_models import (
    McpToolContent,
    McpToolDiscoveryItem,
    McpToolResponse,
    McpToolsListResponse,
)

# Ollama boundary models exports (Ollama API boundary models)
from github_mingzilla.llm_mcp.boundary_models.ollama_boundary_models import (
    OllamaModel,
    OllamaModelsResponse,
)

# OpenAI boundary models exports (OpenAI API boundary models)
from github_mingzilla.llm_mcp.boundary_models.openai_boundary_models import (
    OpenAIMessage,
    OpenAIToolCall,
)

# All models available at package level
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
]
