import os
from typing import Any, AsyncGenerator, Dict, List, Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

from github_mingzilla.llm_mcp.models.chat_models import ChatMessage, StreamChunk
from github_mingzilla.llm_mcp.models.llm_models import LlmResponse
from github_mingzilla.llm_mcp.util.llm_openai_util import LlmOpenaiUtil

load_dotenv()


class LLMClient:
    """OpenAI client wrapper for LLM interactions with streaming support."""

    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = os.getenv("LLM_MODEL", "gpt-4.1-nano")

    async def chat_completion(self, messages: List[ChatMessage], model: Optional[str], mcp_tools: Optional[List[Dict[str, Any]]]) -> LlmResponse:
        """
        Generate chat completion using OpenAI API.

        Args:
            messages: List of chat messages
            model: Optional model override
            mcp_tools: Optional mcp tools

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

            # Convert OpenAI response to generic LlmResponse
            openai_message = response.choices[0].message
            return LlmOpenaiUtil.openai_response_to_llm_response(openai_message)

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    async def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        session_id: str,
        model: Optional[str],
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Generate streaming chat completion using OpenAI API.
        No tools - pure streaming for real-time response.

        Args:
            messages: List of chat messages
            session_id: Session ID for tracking
            model: Optional model override

        Yields:
            StreamChunk objects with content pieces
        """
        model = model or self.default_model
        openai_messages = LlmOpenaiUtil.chat_messages_to_openai_format(messages)

        try:
            completion_kwargs = {
                "model": model,
                "messages": openai_messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 2000,
            }
            # No tools in streaming mode

            response = await self.client.chat.completions.create(**completion_kwargs)

            async for chunk in response:
                delta = chunk.choices[0].delta

                # Handle regular content only (no tool calls in streaming)
                if delta.content is not None:
                    content = delta.content
                    finished = chunk.choices[0].finish_reason is not None

                    yield StreamChunk(
                        content=content,
                        session_id=session_id,
                        finished=finished,
                        metadata={
                            "model": model,
                            "finish_reason": chunk.choices[0].finish_reason,
                        },
                    )

                # Handle finish reasons
                elif chunk.choices[0].finish_reason is not None:
                    # Emit final chunk
                    yield StreamChunk(
                        content="",
                        session_id=session_id,
                        finished=True,
                        metadata={
                            "model": model,
                            "finish_reason": chunk.choices[0].finish_reason,
                        },
                    )

        except Exception as e:
            # Yield error chunk
            yield StreamChunk(
                content=f"Error: {str(e)}",
                session_id=session_id,
                finished=True,
                metadata={"error": True},
            )

    async def test_connection(self) -> bool:
        """
        Test OpenAI API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test with minimal token usage
            test_messages = [ChatMessage(role="user", content="Hello")]
            response = await self.chat_completion(messages=test_messages, model=None, mcp_tools=None)
            return len(response.content or "") > 0
        except Exception:
            return False
