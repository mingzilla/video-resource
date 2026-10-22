import os
from typing import List, Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

from github_mingzilla.llm_mcp.llm_clients.abstract_llm_client import AbstractLlmClient
from github_mingzilla.llm_mcp.models import ApiChatMessage, DomainMcpTool, LlmResponse, OpenAIMessage
from github_mingzilla.llm_mcp.util.llm_openai_util import LlmOpenaiUtil

load_dotenv()


class LLMOpenAIClient(AbstractLlmClient):
    """Original direct OpenAI client implementation for backward compatibility."""

    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = os.getenv("LLM_MODEL", "gpt-4.1-nano")

    async def chat_completion(self, messages: List[ApiChatMessage], model: Optional[str], mcp_tools: Optional[List[DomainMcpTool]]) -> LlmResponse:
        """
        Generate chat completion using OpenAI API.

        Args:
            messages: List of chat messages
            model: Optional model override
            mcp_tools: Optional list of DomainMcpTool objects

        Returns:
            Generic LlmResponse object (provider-agnostic)
        """
        model = model or self.default_model
        openai_messages = LlmOpenaiUtil.chat_messages_to_openai_format(messages)

        try:
            completion_kwargs = {
                "model": model,
                "messages": openai_messages,
                "stream": False,
                "temperature": 0.7,
            }

            # Add tools if provided
            if mcp_tools:
                tools = LlmOpenaiUtil.mcp_to_openai_functions(mcp_tools)
                completion_kwargs["tools"] = tools
                completion_kwargs["tool_choice"] = "auto"

            response = await self.client.chat.completions.create(**completion_kwargs)

            # External library boundary - get raw OpenAI message
            raw_openai_message = response.choices[0].message

            # Convert to typed model at boundary
            typed_message = OpenAIMessage.from_dict(raw_openai_message)

            # Use typed message in utility conversion
            return LlmOpenaiUtil.openai_response_to_llm_response(typed_message, model=model, provider="openai")

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    async def test_connection(self) -> bool:
        """
        Test OpenAI API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test with minimal token usage
            test_messages = [ApiChatMessage(role="user", content="Hello")]
            response = await self.chat_completion(messages=test_messages, model=None, mcp_tools=None)
            return len(response.content or "") > 0
        except Exception:
            return False
