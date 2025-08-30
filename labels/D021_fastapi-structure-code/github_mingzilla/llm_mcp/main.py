"""
Main FastAPI application with refactored service architecture.

This file replaces the monolithic llm_mcp_server.py with a proper layered architecture:
- Router layer for HTTP concerns
- Service layer for business logic
- Repository layer for data access
- Client layer for external integrations

All shared resources use singleton pattern for efficiency.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from github_mingzilla.llm_mcp.routers.chat_router import chat_router
from github_mingzilla.llm_mcp.routers.conversation_router import conversation_router
from github_mingzilla.llm_mcp.routers.health_router import health_router
from github_mingzilla.llm_mcp.routers.root_router import root_router
from github_mingzilla.llm_mcp.routers.tool_router import tool_router
from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifespan and cleanup resources."""
    # Startup
    print("Starting LLM-MCP Integration Server...")

    print(f"Singleton manager initialized with {singleton_manager.get_registered_count()} registered services")
    print(f"Services with cleanup: {singleton_manager.get_closable_count()}")
    print("Services will be initialized on first use (lazy loading)")

    yield

    # Shutdown
    print("Shutting down LLM-MCP Integration Server...")
    await singleton_manager.shutdown_all()


# FastAPI app instance
app = FastAPI(
    title="LLM-MCP Integration Server",
    description="Server 1: LLM + MCP Client for natural language API interaction",
    version="2.0.0",
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

# Register routers
app.include_router(root_router)
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(tool_router)
app.include_router(conversation_router)

# Mount static files (placed after all API routes to ensure API takes precedence)
app.mount("/app", StaticFiles(directory="static", html=True), name="app")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
