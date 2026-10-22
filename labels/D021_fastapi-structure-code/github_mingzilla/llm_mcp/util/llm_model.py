"""LLM Model configuration utility with enum-like behavior for model-to-provider mapping."""

import os
from dataclasses import dataclass
from typing import Dict

# Class-level cache for model configurations
_MODEL_CACHE: Dict[str, "LlmModel"] = {}


@dataclass
class LlmModel:
    """Configuration for a specific LLM model including provider and endpoints."""

    provider: str
    batch_url: str
    stream_url: str
    model_name: str

    @staticmethod
    def get_by_model(model_name: str) -> "LlmModel":
        """
        Get LLM model configuration by model name.

        Args:
            model_name: Name of the model (e.g., 'tinyllama', 'gpt-4o-mini')

        Returns:
            LlmModel instance with provider and endpoint configuration

        Raises:
            ValueError: If model name is not supported
        """
        if not model_name:
            # Use fallback for empty model name
            model_name = os.getenv("OLLAMA_MODEL", "tinyllama")

        # Check cache first
        if model_name in _MODEL_CACHE:
            return _MODEL_CACHE[model_name]

        # Determine provider and configuration based on model name
        if model_name.startswith(("gpt-", "o1-", "chatgpt-")):
            config = LlmModel._create_openai_direct_config(model_name)
        elif model_name in ["tinyllama", "qwen2.5:3b"]:
            config = LlmModel._create_ollama_config(model_name)
        else:
            config = LlmModel._create_ollama_config(model_name)

        # Cache the configuration
        _MODEL_CACHE[model_name] = config
        return config

    @staticmethod
    def _create_openai_config(model_name: str) -> "LlmModel":
        """Create OpenAI provider configuration (PydanticAI - no function calling)."""
        return LlmModel(provider="openai", batch_url="https://api.openai.com/v1/chat/completions", stream_url="https://api.openai.com/v1/chat/completions", model_name=model_name)

    @staticmethod
    def _create_openai_direct_config(model_name: str) -> "LlmModel":
        """Create OpenAI Direct provider configuration (with function calling support)."""
        return LlmModel(provider="openai", batch_url="https://api.openai.com/v1/chat/completions", stream_url="https://api.openai.com/v1/chat/completions", model_name=model_name)

    @staticmethod
    def _create_ollama_config(model_name: str) -> "LlmModel":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        base_url = base_url.rstrip("/")
        return LlmModel(provider="ollama", batch_url=f"{base_url}/v1/chat/completions", stream_url=f"{base_url}/v1/chat/completions", model_name=model_name)

    def get_headers(self) -> Dict[str, str]:
        """Get appropriate headers for this model's provider."""
        if self.provider in ["openai"]:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable required for OpenAI models")
            return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        elif self.provider == "ollama":
            return {"Content-Type": "application/json"}
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    @staticmethod
    def clear_cache():
        """Clear the model configuration cache (useful for testing)."""
        _MODEL_CACHE.clear()

    @staticmethod
    def get_supported_models() -> Dict[str, str]:
        """Get dictionary of supported models and their providers."""
        return {
            # OpenAI models (using openai for function calling support)
            "gpt-4o": "openai",
            "gpt-4o-mini": "openai",
            "gpt-4": "openai",
            "gpt-4-turbo": "openai",
            "gpt-3.5-turbo": "openai",
            "o1-preview": "openai",
            "o1-mini": "openai",
            # Ollama models
            "tinyllama": "ollama",
            "qwen2.5:3b": "ollama",
        }
