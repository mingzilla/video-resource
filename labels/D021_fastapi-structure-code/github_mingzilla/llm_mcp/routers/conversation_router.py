"""
FastAPI router for conversation endpoints.

Handles HTTP concerns for conversation management functionality, delegating business logic to ConversationService.
"""

from fastapi import APIRouter, HTTPException, Request

from github_mingzilla.llm_mcp.services.conversation_service import conversation_service

router = APIRouter(prefix="/api/v1", tags=["conversation"])


@router.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    try:
        conversation_data = conversation_service.get_conversation_details(session_id)

        return conversation_data

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.delete("/conversation/{session_id}")
async def delete_conversation(session_id: str):
    """Delete conversation history for a session."""
    try:
        success = conversation_service.delete_conversation(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": f"Conversation {session_id} deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")


@router.post("/conversation/{session_id}/message")
async def add_message_to_conversation(session_id: str, request: Request):
    """
    Add accumulated message to conversation history.

    Used by optimized streaming clients to submit complete assistant messages
    after accumulating chunks client-side.

    Security: In production, add authentication/authorization here.
    """
    try:
        body = await request.json()

        result = conversation_service.add_message_to_conversation(session_id, body)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


# Module-level singleton instance
conversation_router = router
