"""
FastAPI router for chat endpoints.

Handles HTTP concerns for chat functionality, delegating business logic to ChatService.
"""

from fastapi import APIRouter, HTTPException, Request
from sse_starlette import EventSourceResponse

from github_mingzilla.llm_mcp.boundary_models import ApiChatRequest, ApiChatResponse
from github_mingzilla.llm_mcp.services.chat_service import chat_service

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ApiChatResponse)
async def chat(chat_request: ApiChatRequest):
    """
    Batch request without streaming.
    """
    try:
        # Validate request
        chat_service.validate_chat_request(chat_request, require_tools=False)

        # Handle chat request
        response = await chat_service.handle_batch_chat(chat_request)
        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(chat_request: ApiChatRequest, request: Request):
    """
    SSE streaming chat endpoint for pure text streaming (no tools).
    - Always returns Server-Sent Events (SSE)
    - Returns real-time text chunks without tool orchestration
    - For tool-enabled chat, use /api/v1/chat/stream-tools endpoint

    Requires client to send: Accept: text/event-stream
    """
    try:
        # Validate Accept header and request
        accept_header = request.headers.get("accept", "")
        chat_service.validate_sse_headers(accept_header)
        chat_service.validate_chat_request(chat_request, require_tools=False)

        # Check if tools are requested - redirect to appropriate endpoint
        if chat_request.selected_tools:
            raise HTTPException(status_code=400, detail="Tools are not supported on this endpoint. Use /api/v1/chat/stream-tools for tool-enabled chat.")

        # Handle streaming chat
        return EventSourceResponse(chat_service.handle_streaming_chat(chat_request))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream error: {str(e)}")


@router.post("/chat/stream-tools")
async def chat_stream_tools(chat_request: ApiChatRequest, request: Request):
    """
    SSE streaming chat endpoint with tool orchestration.
    - Always returns Server-Sent Events (SSE)
    - Requires tools to be specified in selected_tools
    - SSE events contain complete JSON responses with tool execution results

    Requires client to send: Accept: text/event-stream
    """
    try:
        # Validate Accept header and request
        accept_header = request.headers.get("accept", "")
        chat_service.validate_sse_headers(accept_header)
        chat_service.validate_chat_request(chat_request, require_tools=True)

        # Handle tool orchestration
        return EventSourceResponse(chat_service.handle_tool_orchestration(chat_request))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool orchestration error: {str(e)}")


# Module-level singleton instance
chat_router = router
