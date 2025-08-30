"""
FastAPI router for root endpoints.

Handles informational endpoints like root documentation.
"""

from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "message": "LLM-MCP Integration Server (Server 1)",
        "version": "1.0.0",
        "phase": "2 - MCP Integration with Conversation Storage",
        "endpoints": {
            "health": "/health",
            "chat": "/api/v1/chat",
            "chat_stream": "/api/v1/chat/stream",
            "chat_stream_tools": "/api/v1/chat/stream-tools",
            "conversation": "/api/v1/conversation/{session_id}",
            "tools": "/api/v1/tools",
        },
    }


# Module-level singleton instance
root_router = router
