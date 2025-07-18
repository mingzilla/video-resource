"""
FastAPI router for tool endpoints.

Handles HTTP concerns for tool discovery functionality, delegating business logic to ToolOrchestrationService.
"""

from fastapi import APIRouter, HTTPException

from github_mingzilla.llm_mcp.services.tool_orchestration_service import tool_orchestration_service

router = APIRouter(prefix="/api/v1", tags=["tools"])


@router.get("/tools")
async def get_tools():
    """Get available MCP tools from all servers."""
    try:
        tool_service = tool_orchestration_service
        tools_data = await tool_service.discover_available_tools()

        return tools_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")


# Module-level singleton instance
tool_router = router
