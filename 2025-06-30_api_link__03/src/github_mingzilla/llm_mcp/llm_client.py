# Standard Library
import os
from typing import AsyncGenerator, List, Optional

# Third Party
from dotenv import load_dotenv
from openai import AsyncOpenAI

# First Party
from github_mingzilla.llm_mcp.models.chat_models import ChatMessage, StreamChunk

load_dotenv()


class LLMClient:
    """OpenAI client wrapper for LLM interactions with streaming support."""

    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = os.getenv("LLM_MODEL", "gpt-4-1106-preview")

    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: Optional[str],
        stream: bool,
        tools: Optional[List[dict]]
    ) -> str:
        """
        Generate chat completion using OpenAI API.

        Args:
            messages: List of chat messages
            model: Optional model override
            stream: Whether to stream the response
            tools: Optional OpenAI function definitions for tool calling

        Returns:
            Complete response content
        """
        model = model or self.default_model

        # Convert ChatMessage to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_msg = {"role": msg.role}

            # Add content if present
            if msg.content is not None:
                openai_msg["content"] = msg.content

            # Add tool calls for assistant messages
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls

            # Add tool call info for tool messages
            if msg.role == "tool":
                openai_msg["tool_call_id"] = msg.tool_call_id
                if msg.name:
                    openai_msg["name"] = msg.name

            openai_messages.append(openai_msg)

        try:
            completion_kwargs = {
                "model": model,
                "messages": openai_messages,
                "stream": stream,
                "temperature": 0.7,
                "max_tokens": 2000
            }

            # Add tools if provided
            if tools:
                completion_kwargs["tools"] = tools
                completion_kwargs["tool_choice"] = "auto"

            response = await self.client.chat.completions.create(**completion_kwargs)

            if stream:
                # For streaming, this method shouldn't be used
                # Use chat_completion_stream instead
                raise ValueError("Use chat_completion_stream for streaming responses")

            message = response.choices[0].message
            return message.content or ""

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    async def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        session_id: str,
        model: Optional[str],
        tools: Optional[List[dict]]
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Generate streaming chat completion using OpenAI API.

        Args:
            messages: List of chat messages
            session_id: Session ID for tracking
            model: Optional model override
            tools: Optional OpenAI function definitions for tool calling

        Yields:
            StreamChunk objects with content pieces
        """
        model = model or self.default_model

        # Convert ChatMessage to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_msg = {"role": msg.role}

            # Add content if present
            if msg.content is not None:
                openai_msg["content"] = msg.content

            # Add tool calls for assistant messages
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls

            # Add tool call info for tool messages
            if msg.role == "tool":
                openai_msg["tool_call_id"] = msg.tool_call_id
                if msg.name:
                    openai_msg["name"] = msg.name

            openai_messages.append(openai_msg)

        try:
            completion_kwargs = {
                "model": model,
                "messages": openai_messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 2000
            }

            # Add tools if provided
            if tools:
                completion_kwargs["tools"] = tools
                completion_kwargs["tool_choice"] = "auto"

            response = await self.client.chat.completions.create(**completion_kwargs)

            # Track tool calls across chunks
            tool_calls_buffer = {}

            async for chunk in response:
                delta = chunk.choices[0].delta

                # Handle regular content
                if delta.content is not None:
                    content = delta.content
                    finished = chunk.choices[0].finish_reason is not None

                    yield StreamChunk(
                        content=content,
                        session_id=session_id,
                        finished=finished,
                        metadata={
                            "model": model,
                            "finish_reason": chunk.choices[0].finish_reason
                        }
                    )

                # Handle tool calls - accumulate across chunks
                elif delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        index = tool_call_delta.index

                        # Initialize tool call buffer for this index
                        if index not in tool_calls_buffer:
                            tool_calls_buffer[index] = {
                                "id": "",
                                "function_name": "",
                                "arguments": ""
                            }

                        # Accumulate tool call data
                        if tool_call_delta.id:
                            tool_calls_buffer[index]["id"] = tool_call_delta.id

                        if tool_call_delta.function:
                            if tool_call_delta.function.name:
                                tool_calls_buffer[index]["function_name"] = tool_call_delta.function.name
                            if tool_call_delta.function.arguments:
                                tool_calls_buffer[index]["arguments"] += tool_call_delta.function.arguments

                # Handle finish reasons - emit complete tool calls when done
                if chunk.choices[0].finish_reason is not None:
                    # Emit any complete tool calls
                    for index, tool_call_data in tool_calls_buffer.items():
                        if tool_call_data["function_name"] and tool_call_data["arguments"]:
                            tool_info = {
                                "type": "tool_call",
                                "tool_call_id": tool_call_data["id"],
                                "function_name": tool_call_data["function_name"],
                                "arguments": tool_call_data["arguments"]
                            }

                            yield StreamChunk(
                                content=f"[TOOL_CALL] {tool_call_data['function_name']}",
                                session_id=session_id,
                                finished=False,
                                metadata={
                                    "model": model,
                                    "tool_call": tool_info
                                }
                            )

                    # Emit final chunk
                    yield StreamChunk(
                        content="",
                        session_id=session_id,
                        finished=True,
                        metadata={
                            "model": model,
                            "finish_reason": chunk.choices[0].finish_reason
                        }
                    )

        except Exception as e:
            # Yield error chunk
            yield StreamChunk(
                content=f"Error: {str(e)}",
                session_id=session_id,
                finished=True,
                metadata={"error": True}
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
            response = await self.chat_completion(
                messages=test_messages,
                model=None,
                stream=False,
                tools=None
            )
            return len(response) > 0
        except Exception:
            return False
