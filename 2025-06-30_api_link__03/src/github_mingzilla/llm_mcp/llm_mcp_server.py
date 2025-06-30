# Standard Library
import uuid
from typing import AsyncGenerator, Dict

# Third Party
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse

# First Party
from github_mingzilla.llm_mcp.llm_client import LLMClient
from github_mingzilla.llm_mcp.mcp_client import MCPClient
from github_mingzilla.llm_mcp.models.chat_models import ChatMessage, ChatRequest, ChatResponse
from github_mingzilla.llm_mcp.models.conversation_storage import ConversationStorage

# FastAPI app instance
app = FastAPI(
    title="LLM-MCP Integration Server",
    description="Server 1: LLM + MCP Client for natural language API interaction",
    version="1.0.0"
)

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize clients and storage
llm_client = LLMClient()
mcp_client = MCPClient()
conversation_storage = ConversationStorage()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "components": {}
    }

    try:
        # Test LLM client
        llm_healthy = await llm_client.test_connection()
        health_status["components"]["llm"] = {
            "status": "healthy" if llm_healthy else "unhealthy",
            "details": "OpenAI client connection"
        }
    except Exception as e:
        health_status["components"]["llm"] = {
            "status": "error",
            "details": f"LLM client error: {str(e)}"
        }
        llm_healthy = False

    try:
        # Test MCP client
        mcp_healthy = await mcp_client.test_connection()
        health_status["components"]["mcp"] = {
            "status": "healthy" if mcp_healthy else "unhealthy",
            "details": f"MCP server at {mcp_client.server_url}"
        }
    except Exception as e:
        health_status["components"]["mcp"] = {
            "status": "error",
            "details": f"MCP client error: {str(e)}"
        }
        mcp_healthy = False

    # Overall status - service is available even if some components are down
    overall_healthy = llm_healthy or mcp_healthy  # At least one should work
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    health_status["overall_healthy"] = overall_healthy

    return health_status


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """
    Basic chat endpoint without streaming.
    For testing purposes in Phase 1+2.
    """
    try:
        # Generate or use provided session ID
        session_id = chat_request.session_id or str(uuid.uuid4())

        # Add user message to history
        user_message = ChatMessage(role="user", content=chat_request.message)
        conversation_storage.add_message(session_id, user_message)

        # Get conversation history
        conversation = conversation_storage.get_or_create_conversation(session_id)

        # Get available tools from MCP server
        tools = await mcp_client.get_openai_functions()

        # Get LLM response with tools if available
        response_content = await llm_client.chat_completion(
            messages=conversation,
            model=chat_request.model,
            stream=False,
            tools=tools if tools else None
        )

        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=response_content)
        conversation_storage.add_message(session_id, assistant_message)

        return ChatResponse(
            response=response_content,
            session_id=session_id,
            model=chat_request.model or "gpt-4-1106-preview"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/api/v1/chat/stream")
async def chat_stream(chat_request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events.
    Main endpoint for real-time LLM interaction with MCP tool calling.
    """
    try:
        # Generate or use provided session ID
        session_id = chat_request.session_id or str(uuid.uuid4())

        # Add user message to history
        user_message = ChatMessage(role="user", content=chat_request.message)
        conversation_storage.add_message(session_id, user_message)

        stream_generator = _handle_stream_and_add_accumulated_content_to_conversation(
            session_id=session_id,
            model=chat_request.model
        )

        return EventSourceResponse(stream_generator)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream error: {str(e)}")


async def _handle_stream_and_add_accumulated_content_to_conversation(session_id: str, model: str) -> AsyncGenerator[Dict[str, str], None]:
    """
    Generate SSE stream for chat response.

    Args:
        session_id: The session ID for the conversation
        model: The model to use for completion

    Yields:
        SSE events for streaming response
    """
    accumulated_content = ""

    try:
        # Get conversation history
        conversation = conversation_storage.get_or_create_conversation(session_id)

        # Get available tools from MCP server
        tools = await mcp_client.get_openai_functions()

        async for chunk in llm_client.chat_completion_stream(
                messages=conversation,
                session_id=session_id,
                model=model,
                tools=tools if tools else None
        ):
            # Handle tool calls
            if chunk.metadata.get("tool_call"):
                tool_call_info = chunk.metadata["tool_call"]
                try:
                    # Execute the tool call via MCP
                    # Standard Library
                    import json
                    arguments = json.loads(tool_call_info["arguments"])
                    tool_result = await mcp_client.call_tool(
                        tool_call_info["function_name"],
                        arguments
                    )

                    # Add tool call to conversation history
                    tool_call_message = ChatMessage(
                        role="assistant",
                        content=None,
                        tool_calls=[{
                            "id": tool_call_info["tool_call_id"],
                            "type": "function",
                            "function": {
                                "name": tool_call_info["function_name"],
                                "arguments": tool_call_info["arguments"]
                            }
                        }]
                    )
                    conversation_storage.add_message(session_id, tool_call_message)

                    # Add tool result to conversation history
                    tool_result_message = ChatMessage(
                        role="tool",
                        content=json.dumps(tool_result),
                        tool_call_id=tool_call_info["tool_call_id"],
                        name=tool_call_info["function_name"]
                    )
                    conversation_storage.add_message(session_id, tool_result_message)

                    # Send tool result as special event
                    yield {
                        "event": "tool_result",
                        "data": json.dumps({
                            "tool_call_id": tool_call_info["tool_call_id"],
                            "function_name": tool_call_info["function_name"],
                            "result": tool_result
                        })
                    }
                except Exception as tool_error:
                    # Add error to conversation history
                    error_message = ChatMessage(
                        role="tool",
                        content=f"Error: {str(tool_error)}",
                        tool_call_id=tool_call_info["tool_call_id"],
                        name=tool_call_info["function_name"]
                    )
                    conversation_storage.add_message(session_id, error_message)

                    yield {
                        "event": "tool_error",
                        "data": json.dumps({
                            "tool_call_id": tool_call_info["tool_call_id"],
                            "function_name": tool_call_info["function_name"],
                            "error": str(tool_error)
                        })
                    }

            # Accumulate content for conversation history
            if not chunk.metadata.get("error") and not chunk.metadata.get("tool_call"):
                accumulated_content += chunk.content

            # Send chunk as SSE event
            yield {
                "event": "chunk",
                "data": chunk.model_dump_json()
            }

            # If finished, break the loop
            if chunk.finished:
                break

    except Exception as e:
        # Send error event
        yield {
            "event": "error",
            "data": f'{{"error": "{str(e)}", "session_id": "{session_id}"}}'
        }

    finally:
        # Add assistant response to conversation history
        if accumulated_content:
            assistant_message = ChatMessage(role="assistant", content=accumulated_content)
            conversation_storage.add_message(session_id, assistant_message)

        # Send completion event
        yield {
            "event": "complete",
            "data": f'{{"session_id": "{session_id}", "total_messages": {conversation_storage.get_message_count(session_id)}}}'
        }


@app.get("/api/v1/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    conversation = conversation_storage.get_conversation(session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": [msg.dict() for msg in conversation],
        "message_count": conversation_storage.get_message_count(session_id)
    }


@app.delete("/api/v1/conversation/{session_id}")
async def delete_conversation(session_id: str):
    """Delete conversation history for a session."""
    if not conversation_storage.delete_conversation(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": f"Conversation {session_id} deleted"}


@app.get("/api/v1/tools")
async def get_tools():
    """Get available MCP tools in OpenAI function format."""
    try:
        tools = await mcp_client.get_openai_functions()
        return {
            "tools": tools,
            "count": len(tools),
            "mcp_server": mcp_client.server_url
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
            "result": result
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
            "call_tool": "/api/v1/tools/call"
        }
    }


if __name__ == "__main__":
    # Third Party
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
