from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

# MCP
from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from github_mingzilla.api_link.core.database import Database
from github_mingzilla.api_link.core.repo_util import RepoUtil
from github_mingzilla.api_link.models.entities.api_config import ApiConfigCreate, ApiConfigEntity, ApiConfigUpdate


@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Async context manager for database session."""
    async for session in Database.get_session():
        yield session


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[callable]:
    """Async lifecycle management - yield context manager function."""
    # Test database connection on startup
    if not await Database.test_connection():
        raise RuntimeError("Failed to connect to database")

    yield get_db_session  # Yield the async context manager function


# Create MCP server with async lifespan
mcp = FastMCP("ApiConfigServer", lifespan=app_lifespan, stateless_http=True)


@mcp.tool()
async def create_api_config(name: str, endpoint: str, method: str, description: Optional[str] = None, headers: Optional[Dict[str, Any]] = None, body_template: Optional[str] = None, params: Optional[Dict[str, Any]] = None, ctx: Context = None) -> Dict[str, Any]:
    """Create a new API configuration.

    Args:
        name: Unique name for the API configuration
        endpoint: The full URL endpoint for the API request
        method: HTTP method (e.g., GET, POST, PUT, DELETE)
        description: Detailed description of the API configuration
        headers: JSON object storing request headers as key-value pairs
        body_template: Template for the request body, can contain placeholders
        params: JSON object storing query parameters template
        ctx: MCP context for accessing lifecycle resources

    Returns:
        Created API configuration with ID and timestamps
    """
    get_session = ctx.request_context.lifespan_context

    async with get_session() as session:
        # Create Pydantic model
        api_config_create = ApiConfigCreate(name=name, endpoint=endpoint, method=method, description=description, headers=headers, body_template=body_template, params=params)

        # Create entity
        created_api_config = await RepoUtil.create_entity(session, ApiConfigEntity, api_config_create)

        # Convert to dict for JSON response
        return {"id": created_api_config.id, "name": created_api_config.name, "description": created_api_config.description, "endpoint": created_api_config.endpoint, "method": created_api_config.method, "headers": created_api_config.headers, "body_template": created_api_config.body_template, "params": created_api_config.params, "created_at": created_api_config.created_at.isoformat(), "updated_at": created_api_config.updated_at.isoformat()}


@mcp.tool()
async def get_api_config(api_config_id: int, ctx: Context) -> Dict[str, Any]:
    """Retrieve an API configuration by ID.

    Args:
        api_config_id: ID of the API configuration to retrieve
        ctx: MCP context for accessing lifecycle resources

    Returns:
        API configuration details

    Raises:
        RuntimeError: If API configuration not found
    """
    get_session = ctx.request_context.lifespan_context

    async with get_session() as session:
        db_api_config = await RepoUtil.get_by_id(session, ApiConfigEntity, api_config_id)
        if db_api_config is None:
            raise RuntimeError(f"ApiConfig with id {api_config_id} not found")

        return {"id": db_api_config.id, "name": db_api_config.name, "description": db_api_config.description, "endpoint": db_api_config.endpoint, "method": db_api_config.method, "headers": db_api_config.headers, "body_template": db_api_config.body_template, "params": db_api_config.params, "created_at": db_api_config.created_at.isoformat(), "updated_at": db_api_config.updated_at.isoformat()}


@mcp.tool()
async def get_all_api_configs(limit: int = 100, offset: int = 0, ctx: Context = None) -> List[Dict[str, Any]]:
    """Retrieve all API configurations with pagination.

    Args:
        limit: Maximum number of records to return (default: 100)
        offset: Number of records to skip (default: 0)
        ctx: MCP context for accessing lifecycle resources

    Returns:
        List of API configuration details
    """
    get_session = ctx.request_context.lifespan_context

    async with get_session() as session:
        api_configs = await RepoUtil.get_limited(session, ApiConfigEntity, limit, offset)

        return [{"id": config.id, "name": config.name, "description": config.description, "endpoint": config.endpoint, "method": config.method, "headers": config.headers, "body_template": config.body_template, "params": config.params, "created_at": config.created_at.isoformat(), "updated_at": config.updated_at.isoformat()} for config in api_configs]


@mcp.tool()
async def update_api_config(api_config_id: int, name: Optional[str] = None, endpoint: Optional[str] = None, method: Optional[str] = None, description: Optional[str] = None, headers: Optional[Dict[str, Any]] = None, body_template: Optional[str] = None, params: Optional[Dict[str, Any]] = None, ctx: Context = None) -> Dict[str, Any]:
    """Update an existing API configuration.

    Args:
        api_config_id: ID of the API configuration to update
        name: Updated name for the API configuration
        endpoint: Updated endpoint URL
        method: Updated HTTP method
        description: Updated description
        headers: Updated headers
        body_template: Updated body template
        params: Updated parameters
        ctx: MCP context for accessing lifecycle resources

    Returns:
        Updated API configuration details

    Raises:
        RuntimeError: If API configuration not found
    """
    get_session = ctx.request_context.lifespan_context

    async with get_session() as session:
        # Create update model with only provided fields
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if endpoint is not None:
            update_data["endpoint"] = endpoint
        if method is not None:
            update_data["method"] = method
        if description is not None:
            update_data["description"] = description
        if headers is not None:
            update_data["headers"] = headers
        if body_template is not None:
            update_data["body_template"] = body_template
        if params is not None:
            update_data["params"] = params

        if not update_data:
            raise RuntimeError("No update data provided")

        api_config_update = ApiConfigUpdate(**update_data)

        updated_api_config = await RepoUtil.merge_entity(session, ApiConfigEntity, api_config_id, api_config_update)
        if updated_api_config is None:
            raise RuntimeError(f"ApiConfig with id {api_config_id} not found for update")

        return {"id": updated_api_config.id, "name": updated_api_config.name, "description": updated_api_config.description, "endpoint": updated_api_config.endpoint, "method": updated_api_config.method, "headers": updated_api_config.headers, "body_template": updated_api_config.body_template, "params": updated_api_config.params, "created_at": updated_api_config.created_at.isoformat(), "updated_at": updated_api_config.updated_at.isoformat()}


@mcp.tool()
async def delete_api_config(api_config_id: int, ctx: Context) -> Dict[str, str]:
    """Delete an API configuration by ID.

    Args:
        api_config_id: ID of the API configuration to delete
        ctx: MCP context for accessing lifecycle resources

    Returns:
        Confirmation message

    Raises:
        RuntimeError: If API configuration not found
    """
    get_session = ctx.request_context.lifespan_context

    async with get_session() as session:
        deleted_api_config = await RepoUtil.delete(session, ApiConfigEntity, api_config_id)
        if deleted_api_config is None:
            raise RuntimeError(f"ApiConfig with id {api_config_id} not found for deletion")

        return {"message": f"ApiConfig with id {api_config_id} deleted successfully"}


@mcp.resource("config://api-configs/all")
async def get_all_api_configs_resource() -> str:
    """Get all API configurations as a resource."""
    try:
        configs = await get_all_api_configs()
        return f"Total API configurations: {len(configs)}\n\n" + "\n".join([f"ID: {config['id']}, Name: {config['name']}, Method: {config['method']}, Endpoint: {config['endpoint']}" for config in configs])
    except Exception as e:
        return f"Error retrieving API configurations: {str(e)}"


@mcp.resource("config://api-configs/{api_config_id}")
async def get_api_config_resource(api_config_id: str) -> str:
    """Get a specific API configuration as a resource."""
    try:
        config_id = int(api_config_id)
        config = await get_api_config(config_id)
        return f"API Configuration Details:\nID: {config['id']}\nName: {config['name']}\nDescription: {config.get('description', 'N/A')}\nMethod: {config['method']}\nEndpoint: {config['endpoint']}\nHeaders: {config.get('headers', 'N/A')}\nBody Template: {config.get('body_template', 'N/A')}\nParameters: {config.get('params', 'N/A')}\nCreated: {config['created_at']}\nUpdated: {config['updated_at']}"
    except ValueError:
        return f"Invalid API config ID: {api_config_id}"
    except Exception as e:
        return f"Error retrieving API configuration: {str(e)}"


# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
