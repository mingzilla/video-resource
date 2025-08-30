import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sse_starlette import EventSourceResponse

from github_mingzilla.llm_mcp.llm_client import LLMClient
from github_mingzilla.llm_mcp.mcp_client import MCPClient
from github_mingzilla.llm_mcp.models.chat_models import ChatMessage, ChatRequest, ChatResponse
from github_mingzilla.llm_mcp.models.conversation_storage import ConversationStorage


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
conversation_storage = ConversationStorage()


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """
    Batch request without streaming.
    """
    try:
        session_id = chat_request.session_id or str(uuid.uuid4())

        user_message = ChatMessage(role="user", content=chat_request.message)
        conversation_storage.add_message(session_id, user_message)

        conversation = conversation_storage.get_or_create_conversation(session_id)

        llm_response = await llm_client.chat_completion(messages=conversation, model=chat_request.model, mcp_tools=None)
        response_content = llm_response.content or ""

        assistant_message = ChatMessage(role="assistant", content=response_content)
        conversation_storage.add_message(session_id, assistant_message)

        return ChatResponse(
            response=response_content,
            session_id=session_id,
            model=chat_request.model or "gpt-4.1-nano",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/api/v1/chat/stream")
async def chat_stream(chat_request: ChatRequest, request: Request):
    """
    SSE streaming chat endpoint.
    - Always returns Server-Sent Events (SSE)
    - With tools: SSE events contain complete JSON responses
    - Without tools: SSE events contain real-time text chunks

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
        # No tools requested - use pure streaming
        return EventSourceResponse(_chat_stream_no_tools(chat_request))


async def _chat_with_tools(chat_request: ChatRequest):
    """
    Tool orchestration with SSE streaming.
    Yields complete JSON responses as SSE events.
    Assumes tools are valid - lets exceptions bubble up if they fail.
    """
    session_id = chat_request.session_id or str(uuid.uuid4())

    try:
        user_message = ChatMessage(role="user", content=chat_request.message)
        conversation_storage.add_message(session_id, user_message)

        filtered_tools = await mcp_client.get_filtered_tools(chat_request.selected_tools)

        # Progressive tool orchestration - yield each LLM response immediately
        async for iteration_response in _handle_tool_orchestration_streaming(session_id=session_id, model=chat_request.model, mcp_tools=filtered_tools, iteration=0):
            # Yield each LLM response as SSE event containing JSON
            chat_response = ChatResponse(
                response=iteration_response,
                session_id=session_id,
                model=chat_request.model or "gpt-4.1-nano",
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


async def _handle_tool_orchestration_streaming(session_id: str, model: str, mcp_tools: List[Dict[str, Any]], iteration: int):
    """
    Progressive tool orchestration following diagram section 2.4.
    Yields each LLM response immediately while continuing tool processing.

    Args:
        session_id: The session ID for the conversation
        model: The model to use for completion
        mcp_tools: Pre-filtered list of MCP tools
        iteration: Current recursion depth (for protection)

    Yields:
        Each LLM response content as it becomes available
    """

    import json

    # Prevent infinite recursion
    if iteration >= 5:
        yield "Maximum tool call iterations reached."
        return

    try:
        # Get conversation history
        conversation = conversation_storage.get_or_create_conversation(session_id)

        # Send conversation + tools to LLM
        llm_response = await llm_client.chat_completion(messages=conversation, model=model, mcp_tools=mcp_tools)

        # Convert generic tool calls to ChatMessage dict format
        tool_calls_dict = llm_response.to_chat_message_dict()

        # Add assistant message to history
        assistant_message = ChatMessage(
            role="assistant",
            content=llm_response.content,
            tool_calls=tool_calls_dict,
        )
        conversation_storage.add_message(session_id, assistant_message)

        yield llm_response.get_status_text()

        if not llm_response.has_tool_calls():
            return

        # Execute each tool call using generic interface
        for tool_data in llm_response.get_tool_execution_data():
            try:
                tool_name = tool_data["name"]
                arguments = json.loads(tool_data["arguments"])
                tool_result = await mcp_client.call_tool(tool_name, arguments)

                tool_message = ChatMessage(
                    role="tool",
                    content=json.dumps(tool_result),
                    tool_call_id=tool_data["id"],
                    name=tool_name,
                )
                conversation_storage.add_message(session_id, tool_message)

            except Exception as e:
                error_message = ChatMessage(
                    role="tool",
                    content=json.dumps({"error": f"Tool execution failed: {str(e)}"}),
                    tool_call_id=tool_data["id"],
                    name=tool_name,
                )
                conversation_storage.add_message(session_id, error_message)

        # Recursive case: tools were called, continue for next LLM round
        async for next_response in _handle_tool_orchestration_streaming(session_id, model, mcp_tools, iteration + 1):
            yield next_response

    except Exception as e:
        yield f"Error during tool orchestration: {str(e)}"


async def _chat_stream_no_tools(chat_request: ChatRequest):
    """
    Pure streaming chat without tools.
    Returns async generator for EventSourceResponse.
    """
    session_id = chat_request.session_id or str(uuid.uuid4())

    try:
        user_message = ChatMessage(role="user", content=chat_request.message)
        conversation_storage.add_message(session_id, user_message)

        # Delegate to the streaming generator
        async for event in _handle_stream_and_add_accumulated_content_to_conversation(session_id, chat_request.model):
            yield event

    except Exception as e:
        # Yield error as SSE event
        yield {
            "event": "error",
            "data": f'{{"error": "Stream error: {str(e)}", "session_id": "{session_id}"}}',
        }


async def _handle_stream_and_add_accumulated_content_to_conversation(session_id: str, model: str) -> AsyncGenerator[Dict[str, str], None]:
    """
    Generate SSE stream for chat response (no tools selected).

    Args:
        session_id: The session ID for the conversation
        model: The model to use for completion

    Yields:
        SSE events for real-time streaming response
    """
    accumulated_content = ""

    try:
        conversation = conversation_storage.get_or_create_conversation(session_id)
        async for chunk in llm_client.chat_completion_stream(
            messages=conversation,
            session_id=session_id,
            model=model,
        ):
            if not chunk.metadata.get("error"):
                accumulated_content += chunk.content

            yield {
                "event": "chunk",
                "data": chunk.model_dump_json(),
            }

            if chunk.finished:
                break

    except Exception as e:
        yield {
            "event": "error",
            "data": f'{{"error": "{str(e)}", "session_id": "{session_id}"}}',
        }

    finally:
        if accumulated_content:
            assistant_message = ChatMessage(role="assistant", content=accumulated_content)
            conversation_storage.add_message(session_id, assistant_message)

        yield {
            "event": "complete",
            "data": f'{{"session_id": "{session_id}", "total_messages": {conversation_storage.get_message_count(session_id)}}}',
        }


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
    conversation = conversation_storage.get_conversation(session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": [msg.dict() for msg in conversation],
        "message_count": conversation_storage.get_message_count(session_id),
    }


@app.delete("/api/v1/conversation/{session_id}")
async def delete_conversation(session_id: str):
    """Delete conversation history for a session."""
    if not conversation_storage.delete_conversation(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": f"Conversation {session_id} deleted"}


@app.get("/api/v1/tools")
async def get_tools():
    """Get available MCP tools from all servers."""
    try:
        tools = await mcp_client.discover_tools()

        # Get server configuration information
        return {
            "tools": tools,
            "count": len(tools),
            "mcp_servers": mcp_client.server_mapping,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")


@app.post("/api/v1/tools/call")
async def call_tool(request: Request):
    """Direct tool calling endpoint for testing."""
    try:
        body = await request.json()
        tool_name = body.get("tool_name")
        arguments = body.get("arguments", {})

        if not tool_name:
            raise HTTPException(status_code=400, detail="tool_name is required")

        result = await mcp_client.call_tool(tool_name, arguments)
        return {
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool call failed: {str(e)}")


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
            "call_tool": "/api/v1/tools/call",
        },
    }


# Mount static files (placed after all API routes to ensure API takes precedence)
app.mount("/app", StaticFiles(directory="static", html=True), name="app")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
