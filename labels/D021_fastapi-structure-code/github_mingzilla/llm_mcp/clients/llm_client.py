from typing import AsyncGenerator, List, Optional

from dotenv import load_dotenv

from github_mingzilla.llm_mcp.clients.http_client import http_client
from github_mingzilla.llm_mcp.models import ApiChatMessage, DomainMcpTool, LlmResponse
from github_mingzilla.llm_mcp.service_manager.interfaces import ClosableService
from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager
from github_mingzilla.llm_mcp.util.llm_model import LlmModel
from github_mingzilla.llm_mcp.util.llm_providers import LLMProviders

load_dotenv()


class _LLMClient(ClosableService):
    """Provider-agnostic LLM client that uses LlmModel utility for per-request configuration."""

    def __init__(self):
        """Initialize LLM client. Configuration determined per request using LlmModel utility."""
        # Ensure fresh configuration by clearing LlmModel cache on initialization
        # This prevents issues where cache was populated before environment variables were loaded
        LlmModel.clear_cache()
        self._providers = LLMProviders()

    async def invoke(self, messages: List[ApiChatMessage], model: Optional[str], mcp_tools: Optional[List[DomainMcpTool]]) -> LlmResponse:
        llm_model = LlmModel.get_by_model(model)
        provider = self._providers.get_by_name(llm_model.provider)
        return await provider.chat_completion(messages=messages, model=llm_model.model_name, mcp_tools=mcp_tools)

    async def raw_stream_openai_format(
        self,
        messages: List[ApiChatMessage],
        model: Optional[str],
    ) -> AsyncGenerator[str, None]:
        """
        Unified streaming method using LlmModel utility for configuration.

        Args:
            messages: List of chat messages
            model: Model name (determines provider and endpoints automatically)

        Yields:
            Raw strings from provider API
        """
        import asyncio
        import json

        from github_mingzilla.llm_mcp.util.llm_openai_util import LlmOpenaiUtil

        llm_model = LlmModel.get_by_model(model)
        openai_messages = LlmOpenaiUtil.chat_messages_to_openai_format(messages)
        payload = {
            "model": llm_model.model_name,
            "messages": openai_messages,
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        async with http_client.create_session() as session:
            try:
                async with session.post(llm_model.stream_url, headers=llm_model.get_headers(), json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        error_chunk = {"error": f"API error {response.status}: {error_text}", "choices": [{"finish_reason": "error"}]}
                        yield json.dumps(error_chunk)
                        return

                    chunk_count = 0

                    # Parse SSE format and yield only JSON data
                    async for line in response.content:
                        chunk_count += 1
                        line_text = line.decode("utf-8").strip()
                        if line_text.startswith("data: "):
                            json_data = line_text[6:]  # Remove "data: " prefix
                            if json_data and json_data != "[DONE]":
                                yield json_data

            except asyncio.CancelledError:
                print(f"🛑 LLM CLIENT DISCONNECTION DETECTED! - streamed {chunk_count} chunks")
                raise  # Re-raise to properly handle the cancellation
            except Exception as e:
                print(f"❌ LLM Client: Unexpected error during streaming: {e}")
                error_chunk = {"error": f"Stream error: {str(e)}", "choices": [{"finish_reason": "error"}]}
                yield json.dumps(error_chunk)

    async def test_connection(self, model: Optional[str] = None) -> bool:
        """
        Test connection for the provider determined by model name using LlmModel utility.

        Args:
            model: Optional model name to determine provider

        Returns:
            True if connection successful, False otherwise
        """
        llm_model = LlmModel.get_by_model(model)
        provider = self._providers.get_by_name(llm_model.provider)
        return await provider.test_connection()

    async def disconnect(self):
        """Disconnect and cleanup LLM client resources."""
        # LLM client doesn't maintain persistent connections
        # but we implement this for interface compliance
        pass


# Module-level singleton instance
llm_client = _LLMClient()
singleton_manager.register(llm_client)
