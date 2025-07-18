"""
Chat service for handling chat business logic.

Coordinates between LLM clients, chat history repository, and tool orchestration.
"""

import uuid
from typing import AsyncGenerator

from github_mingzilla.llm_mcp.boundary_models import ApiChatMessage, ApiChatRequest, ApiChatResponse
from github_mingzilla.llm_mcp.clients.llm_client import llm_client
from github_mingzilla.llm_mcp.clients.mcp_client import mcp_client
from github_mingzilla.llm_mcp.repositories.chat_history_repository import chat_history_repo
from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager


class _ChatService:
    """
    Service for chat operations.
    """

    def __init__(self):
        """Initialize chat service with singleton dependencies."""
        self.llm_client = llm_client
        self.mcp_client = mcp_client
        self.chat_history_repo = chat_history_repo

    async def handle_batch_chat(self, chat_request: ApiChatRequest) -> ApiChatResponse:
        """
        Handle batch (non-streaming) chat request.

        Args:
            chat_request: Chat request with message and configuration

        Returns:
            Complete chat response

        Raises:
            Exception: If chat processing fails
        """
        session_id = chat_request.session_id or str(uuid.uuid4())
        user_message = ApiChatMessage(role="user", content=chat_request.message)

        # Save user message and get conversation history
        messages = self.chat_history_repo.save_message_and_get_history(session_id, user_message)

        # Get LLM response without tools (batch mode doesn't support tools)
        llm_response = await self.llm_client.invoke(messages=messages, model=chat_request.model, mcp_tools=None)
        response_content = llm_response.content or ""

        # Save assistant response
        assistant_message = ApiChatMessage(role="assistant", content=response_content)
        self.chat_history_repo.save_message(session_id, assistant_message)

        return ApiChatResponse(
            response=response_content,
            session_id=session_id,
            model=llm_response.model or "",
            usage=llm_response.usage,
            tool_calls=None,  # Batch mode doesn't support tools
        )

    async def handle_streaming_chat(self, chat_request: ApiChatRequest) -> AsyncGenerator[dict, None]:
        """
        Handle streaming chat request without tools.

        Args:
            chat_request: Chat request with message and configuration

        Yields:
            SSE-formatted chunks with event and data keys

        Raises:
            Exception: If streaming fails
        """
        import asyncio
        import json

        session_id = chat_request.session_id or str(uuid.uuid4())

        try:
            user_message = ApiChatMessage(role="user", content=chat_request.message)
            conversation = self.chat_history_repo.save_message_and_get_history(session_id, user_message)
            model = chat_request.model or "tinyllama"

            print(f"🔄 Starting stream for session {session_id[:8]}... (model: {model})")
            chunk_count = 0

            async for raw_chunk in self.llm_client.raw_stream_openai_format(conversation, model):
                chunk_count += 1
                print(f"📤 Chunk {chunk_count} sent to client (session: {session_id[:8]}...)")
                yield {
                    "event": "chunk",
                    "data": raw_chunk,  # Forward raw JSON string
                }

            print(f"✅ Stream completed normally - {chunk_count} chunks sent (session: {session_id[:8]}...)")

        except asyncio.CancelledError:
            print(f"🛑 CLIENT DISCONNECTED - Stream cancelled after {chunk_count} chunks (session: {session_id[:8]}...)")
            print("   This proves the server detected client disconnection and stopped processing!")
            raise  # Re-raise to properly handle the cancellation
        except NotImplementedError as e:
            print(f"❌ NotImplementedError in stream (session: {session_id[:8]}...): {str(e)}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
        except Exception as e:
            print(f"❌ Stream error (session: {session_id[:8]}...): {str(e)}")
            yield {"event": "error", "data": json.dumps({"error": f"Proxy stream error: {str(e)}", "session_id": session_id})}

    async def handle_tool_orchestration(self, chat_request: ApiChatRequest) -> AsyncGenerator[dict, None]:
        """
        Handle chat request with tool orchestration.

        Args:
            chat_request: Chat request with selected tools

        Yields:
            SSE-formatted responses with tool orchestration results

        Raises:
            Exception: If tool orchestration fails
        """
        session_id = chat_request.session_id or str(uuid.uuid4())

        try:
            user_message = ApiChatMessage(role="user", content=chat_request.message)
            self.chat_history_repo.save_message(session_id, user_message)

            # Get filtered tools
            filtered_tools = await self.mcp_client.get_filtered_tools(chat_request.selected_tools)

            # Import here to avoid circular imports
            from github_mingzilla.llm_mcp.services.tool_orchestration_service import tool_orchestration_service

            tool_service = tool_orchestration_service

            # Progressive tool orchestration - yield each LLM response immediately
            async for iteration_response in tool_service.orchestrate_tools_streaming(session_id=session_id, model=chat_request.model, mcp_tools=filtered_tools, iteration=0):
                # Yield each LLM response as SSE event containing JSON
                chat_response = ApiChatResponse(
                    response=iteration_response.get_status_text(),
                    session_id=session_id,
                    model=iteration_response.model,
                    usage=iteration_response.usage,
                    tool_calls=None,  # Tool calls handled separately in orchestration
                )

                yield {
                    "event": "complete",
                    "data": chat_response.model_dump_json(),
                }

        except Exception as e:
            # Yield error as SSE event
            yield {
                "event": "error",
                "data": f'{{"error": "Chat error: {str(e)}", "session_id": "{session_id}"}}',
            }

    def validate_chat_request(self, chat_request: ApiChatRequest, require_tools: bool = False) -> None:
        """
        Validate chat request parameters.

        Args:
            chat_request: Request to validate
            require_tools: Whether tools are required

        Raises:
            ValueError: If validation fails
        """
        if not chat_request.message or not chat_request.message.strip():
            raise ValueError("Message cannot be empty")

        if require_tools and not chat_request.selected_tools:
            raise ValueError("Tools are required for this endpoint")

        if not require_tools and chat_request.selected_tools:
            raise ValueError("Tools are not supported on this endpoint")

    def validate_sse_headers(self, accept_header: str) -> None:
        """
        Validate that client accepts Server-Sent Events.

        Args:
            accept_header: HTTP Accept header value

        Raises:
            ValueError: If SSE not accepted
        """
        if "text/event-stream" not in accept_header:
            raise ValueError("Accept header must include 'text/event-stream'")

    def _extract_content_from_chunk(self, chunk: str) -> str:
        """
        Extract content from streaming chunk.

        Args:
            chunk: Raw JSON chunk from LLM stream

        Returns:
            Extracted content text
        """
        try:
            import json

            data = json.loads(chunk)
            choices = data.get("choices", [])
            if choices and len(choices) > 0:
                delta = choices[0].get("delta", {})
                return delta.get("content", "")
        except (json.JSONDecodeError, KeyError, IndexError):
            pass
        return ""


# Module-level singleton instance
chat_service = _ChatService()
singleton_manager.register(chat_service)
