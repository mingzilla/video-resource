import os
from typing import List, Optional

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from github_mingzilla.llm_mcp.llm_clients.abstract_llm_client import AbstractLlmClient
from github_mingzilla.llm_mcp.models import ApiChatMessage, DomainMcpTool, LlmResponse

load_dotenv()


class LLMOllamaClient(AbstractLlmClient):
    """PydanticAI-based Ollama client wrapper using OpenAI-compatible API."""

    def __init__(self):
        """Initialize Ollama client with local server configuration."""
        # Ollama OpenAI-compatible configuration
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.base_url = base_url.rstrip("/") + "/v1"
        self.default_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

        # Create OpenAI-compatible provider pointing to Ollama
        self.provider = OpenAIProvider(
            base_url=self.base_url,
            api_key="ollama",  # Ollama doesn't require real API key but PydanticAI expects one
        )

        self.ollama_model = OpenAIModel(model_name=self.default_model, provider=self.provider)

    async def chat_completion(self, messages: List[ApiChatMessage], model: Optional[str], mcp_tools: Optional[List[DomainMcpTool]]) -> LlmResponse:
        """
        Generate chat completion using PydanticAI + Ollama.

        Args:
            messages: List of chat messages
            model: Optional model override
            mcp_tools: Optional mcp tools

        Returns:
            Generic LlmResponse object (provider-agnostic)
        """
        try:
            current_model = model if model else self.default_model
            if current_model != self.ollama_model.model_name:
                self.ollama_model = OpenAIModel(model_name=current_model, provider=self.provider)

            agent = Agent(model=self.ollama_model)
            prompt = self._messages_to_pydantic_format(messages)
            result = await agent.run(prompt)
            content = str(result.data) if result.data else ""

            return LlmResponse(
                content=content,
                tool_calls=[],  # Don't support tool_calls for now
                finish_reason="stop",  # PydanticAI doesn't expose finish_reason directly
                model=model or self.default_model,
                provider="ollama_pydantic",
            )

        except Exception as e:
            raise RuntimeError(f"PydanticAI Ollama error: {str(e)}")

    def _messages_to_pydantic_format(self, messages: List[ApiChatMessage]) -> str:
        """
        Convert ChatMessage objects to prompt format for PydanticAI.
        PydanticAI typically uses a single prompt string, so we'll combine messages.
        """
        prompt_parts = []

        for msg in messages:
            role_prefix = f"{msg.role.upper()}: " if msg.role != "user" else ""
            content = msg.content or ""
            prompt_parts.append(f"{role_prefix}{content}")

        return "\n\n".join(prompt_parts)

    async def test_connection(self) -> bool:
        """
        Test PydanticAI Ollama connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test with minimal prompt
            test_messages = [ApiChatMessage(role="user", content="Hello")]
            response = await self.chat_completion(messages=test_messages, model=None, mcp_tools=None)
            return len(response.content or "") > 0
        except Exception:
            return False
