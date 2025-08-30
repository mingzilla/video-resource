import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sse_starlette import EventSourceResponse

from github_mingzilla.llm_mcp.boundary_models import ApiChatMessage, ApiChatRequest, ApiChatResponse, DomainMcpTool, LlmResponse
from github_mingzilla.llm_mcp.clients.llm_client import _LLMClient as LLMClient
from github_mingzilla.llm_mcp.clients.mcp_client import _MCPClient as MCPClient
from github_mingzilla.llm_mcp.repositories.chat_history_repository import _ChatHistoryRepository as ChatHistoryRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifespan and cleanup resources."""
    # Startup
    print("Starting LLM-MCP Integration Server...")
    yield
    # Shutdown
    print("Shutting down LLM-MCP Integration Server...")
    try:
        if hasattr(app.state, "mcp_client"):
            await app.state.mcp_client.disconnect()
        # Also cleanup the global mcp_client if it exists
        if "mcp_client" in globals():
            await mcp_client.disconnect()
    except Exception as e:
        print(f"Error during shutdown cleanup: {e}")


# FastAPI app instance
app = FastAPI(
    title="LLM-MCP Integration Server",
    description="Server 1: LLM + MCP Client for natural language API interaction",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://127.0.0.1:9000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize clients and storage
llm_client = LLMClient()
mcp_client = MCPClient()
chat_history_repo = ChatHistoryRepository()


@app.post("/api/v1/chat", response_model=ApiChatResponse)
async def chat(chat_request: ApiChatRequest):
    """
    Batch request without streaming.
    """
    try:
        session_id = chat_request.session_id or str(uuid.uuid4())
        user_message = ApiChatMessage(role="user", content=chat_request.message)
        messages = chat_history_repo.save_message_and_get_history(session_id, user_message)

        llm_response = await llm_client.invoke(messages=messages, model=chat_request.model, mcp_tools=None)
        response_content = llm_response.content or ""

        assistant_message = ApiChatMessage(role="assistant", content=response_content)
        chat_history_repo.save_message(session_id, assistant_message)

        return ApiChatResponse(
            response=response_content,
            session_id=session_id,
            model=llm_response.model or "",
            usage=llm_response.usage,
            tool_calls=None,  # Batch mode doesn't support tools
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/api/v1/chat/stream")
async def chat_stream(chat_request: ApiChatRequest, request: Request):
    """
    SSE streaming chat endpoint for pure text streaming (no tools).
    - Always returns Server-Sent Events (SSE)
    - Returns real-time text chunks without tool orchestration
    - For tool-enabled chat, use /api/v1/chat/stream-tools endpoint

    Requires client to send: Accept: text/event-stream
    """
    # Validate Accept header - client must accept SSE format
    accept_header = request.headers.get("accept", "")
    if "text/event-stream" not in accept_header:
        raise HTTPException(status_code=400, detail="Accept header must include 'text/event-stream'")

    # Check if tools are requested - redirect to appropriate endpoint
    if chat_request.selected_tools:
        raise HTTPException(status_code=400, detail="Tools are not supported on this endpoint. Use /api/v1/chat/stream-tools for tool-enabled chat.")

    # Pure streaming without tools
    return EventSourceResponse(_chat_stream_no_tools(chat_request))


@app.post("/api/v1/chat/stream-tools")
async def chat_stream_tools(chat_request: ApiChatRequest, request: Request):
    """
    SSE streaming chat endpoint with tool orchestration.
    - Always returns Server-Sent Events (SSE)
    - Requires tools to be specified in selected_tools
    - SSE events contain complete JSON responses with tool execution results

    Requires client to send: Accept: text/event-stream
    """
    # Validate Accept header - client must accept SSE format
    accept_header = request.headers.get("accept", "")
    if "text/event-stream" not in accept_header:
        raise HTTPException(status_code=400, detail="Accept header must include 'text/event-stream'")

    # Route to appropriate handler based on tool selection
    if chat_request.selected_tools:
        # Tools requested - attempt tool orchestration
        return EventSourceResponse(_chat_with_tools(chat_request))
    else:
        raise HTTPException(status_code=400, detail="Please select tools to be used")


async def _chat_with_tools(chat_request: ApiChatRequest):
    """
    Tool orchestration with SSE streaming.
    Yields complete JSON responses as SSE events.
    Assumes tools are valid - lets exceptions bubble up if they fail.
    """
    session_id = chat_request.session_id or str(uuid.uuid4())

    try:
        user_message = ApiChatMessage(role="user", content=chat_request.message)
        chat_history_repo.save_message(session_id, user_message)

        filtered_tools = await mcp_client.get_filtered_tools(chat_request.selected_tools)

        # Progressive tool orchestration - yield each LLM response immediately
        async for iteration_response in _handle_tool_orchestration_streaming(session_id=session_id, model=chat_request.model, mcp_tools=filtered_tools, iteration=0):
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


async def _handle_tool_orchestration_streaming(session_id: str, model: str, mcp_tools: List[DomainMcpTool], iteration: int) -> AsyncIterator[LlmResponse]:
    """
    Progressive tool orchestration following diagram section 2.4.
    Yields each LLM response immediately while continuing tool processing.

    Args:
        session_id: The session ID for the conversation
        model: The model to use for completion
        mcp_tools: Pre-filtered list of DomainMcpTool objects
        iteration: Current recursion depth (for protection)

    Yields:
        Each LLM response content as it becomes available
    """

    # Prevent infinite recursion
    if iteration >= 5:
        yield "Maximum tool call iterations reached."
        return

    try:
        # Get conversation history
        conversation = chat_history_repo.get_conversation_history(session_id)

        # Send conversation + tools to LLM
        llm_response = await llm_client.invoke(messages=conversation, model=model, mcp_tools=mcp_tools)

        # Convert generic tool calls to ChatMessage dict format
        tool_calls_dict = llm_response.to_chat_message_dict()

        # Add assistant message to history
        assistant_message = ApiChatMessage(
            role="assistant",
            content=llm_response.content,
            tool_calls=tool_calls_dict,
        )
        chat_history_repo.save_message(session_id, assistant_message)

        yield llm_response

        if not llm_response.has_tool_calls():
            return

        # Execute all tool calls in parallel using MCPClient
        tool_messages = await mcp_client.execute_tools_parallel(llm_response.get_tool_execution_data(mcp_tools))

        # Add all tool results to conversation
        for tool_message in tool_messages:
            chat_history_repo.save_message(session_id, tool_message)

        # Recursive case: tools were called, continue for next LLM round
        async for next_response in _handle_tool_orchestration_streaming(session_id, model, mcp_tools, iteration + 1):
            yield next_response

    except Exception as e:
        yield f"Error during tool orchestration: {str(e)}"


async def _chat_stream_no_tools(chat_request: ApiChatRequest):
    """
    Pure streaming chat without tools.

    Server acts as pure proxy - forwards raw LLM chunks without processing.
    Client handles chunk parsing and message accumulation.
    Client must POST accumulated message back via /api/v1/conversation/{session_id}/message

    Performance benefit: Eliminates Python chunk processing overhead.
    """
    import asyncio
    import json

    session_id = chat_request.session_id or str(uuid.uuid4())

    try:
        user_message = ApiChatMessage(role="user", content=chat_request.message)
        conversation = chat_history_repo.save_message_and_get_history(session_id, user_message)
        model = chat_request.model or "tinyllama"

        print(f"🔄 Starting stream for session {session_id[:8]}... (model: {model})")
        chunk_count = 0

        async for raw_chunk in llm_client.raw_stream_openai_format(conversation, model):
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "components": {},
    }

    try:
        # Test LLM client
        llm_healthy = await llm_client.test_connection()
        health_status["components"]["llm"] = {
            "status": "healthy" if llm_healthy else "unhealthy",
            "details": "LLM client connection",
        }
    except Exception as e:
        health_status["components"]["llm"] = {
            "status": "error",
            "details": f"LLM client error: {str(e)}",
        }
        llm_healthy = False

    try:
        # Test MCP client
        mcp_healthy = await mcp_client.test_connection()
        health_status["components"]["mcp"] = {
            "status": "healthy" if mcp_healthy else "unhealthy",
            "details": f"MCP server at {mcp_client.server_url}",
        }
    except Exception as e:
        health_status["components"]["mcp"] = {
            "status": "error",
            "details": f"MCP client error: {str(e)}",
        }
        mcp_healthy = False

    # Overall status - service is available even if some components are down
    overall_healthy = llm_healthy or mcp_healthy  # At least one should work
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    health_status["overall_healthy"] = overall_healthy

    return health_status


@app.get("/api/v1/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    conversation = chat_history_repo.find_conversation_by_id(session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": [msg.dict() for msg in conversation],
        "message_count": chat_history_repo.get_message_count(session_id),
    }


@app.delete("/api/v1/conversation/{session_id}")
async def delete_conversation(session_id: str):
    """Delete conversation history for a session."""
    if not chat_history_repo.delete_conversation(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": f"Conversation {session_id} deleted"}


@app.post("/api/v1/conversation/{session_id}/message")
async def add_message_to_conversation(session_id: str, request: Request):
    """
    Add accumulated message to conversation history.

    Used by optimized streaming clients to submit complete assistant messages
    after accumulating chunks client-side.

    Security: In production, add authentication/authorization here.
    """
    try:
        body = await request.json()

        # Validate required fields
        role = body.get("role")
        content = body.get("content", "")

        if not role:
            raise HTTPException(status_code=400, detail="role is required")

        if role not in ["assistant", "user", "system"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'assistant', 'user', or 'system'")

        if not content.strip():
            raise HTTPException(status_code=400, detail="content cannot be empty")

        # TODO: Add session ownership verification in production
        # user_id = extract_user_from_auth_token(request.headers.get("authorization"))
        # if not verify_session_ownership(session_id, user_id):
        #     raise HTTPException(status_code=403, detail="Not authorized for this session")

        # Add message to conversation
        message = ApiChatMessage(
            role=role,
            content=content,
            tool_calls=body.get("tool_calls"),  # Optional
        )

        chat_history_repo.save_message(session_id, message)

        return {
            "success": True,
            "session_id": session_id,
            "message_count": chat_history_repo.get_message_count(session_id),
            "message": {
                "role": role,
                "content": content[:100] + "..." if len(content) > 100 else content,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@app.get("/api/v1/tools")
async def get_tools():
    """Get available MCP tools from all servers."""
    try:
        tools = await mcp_client.discover_tools()

        # Convert McpTool objects to dict for JSON response
        tools_dict = [tool.model_dump() for tool in tools]

        # Get server configuration information
        return {
            "tools": tools_dict,
            "count": len(tools),
            "mcp_servers": mcp_client.server_mapping,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LLM-MCP Integration Server (Server 1)",
        "version": "1.0.0",
        "phase": "2 - MCP Integration with Conversation Storage",
        "endpoints": {
            "health": "/health",
            "chat": "/api/v1/chat",
            "chat_stream": "/api/v1/chat/stream",
            "conversation": "/api/v1/conversation/{session_id}",
            "tools": "/api/v1/tools",
        },
    }


# Mount static files (placed after all API routes to ensure API takes precedence)
app.mount("/app", StaticFiles(directory="static", html=True), name="app")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
