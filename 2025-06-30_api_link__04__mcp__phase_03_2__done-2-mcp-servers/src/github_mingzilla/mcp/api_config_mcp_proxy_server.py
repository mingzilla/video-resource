from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from github_mingzilla.api_link.models.entities.api_config import ApiConfigCreate, ApiConfigUpdate
from github_mingzilla.mcp.proxy_request import ProxyRequest

# MCP Proxy Server that forwards requests to FastAPI controller
mcp = FastMCP("ApiConfigMcpProxyServer", stateless_http=True)

# Configuration for the FastAPI server
FASTAPI_BASE_URL = "http://127.0.0.1:8001"
API_CONFIG_ENDPOINT = f"{FASTAPI_BASE_URL}/api/v1/api_configs"


@mcp.tool()
async def create_api_config(name: str, endpoint: str, method: str, description: str = None, headers: Dict[str, Any] = None, body_template: str = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a new API configuration via FastAPI proxy."""
    model = ApiConfigCreate(name=name, endpoint=endpoint, method=method, description=description, headers=headers, body_template=body_template, params=params)
    return await ProxyRequest.redirect("POST", f"{API_CONFIG_ENDPOINT}/", model)


@mcp.tool()
async def get_api_config(api_config_id: int) -> Dict[str, Any]:
    """Retrieve an API configuration by ID via FastAPI proxy."""
    return await ProxyRequest.redirect("GET", f"{API_CONFIG_ENDPOINT}/{api_config_id}")


@mcp.tool()
async def get_all_api_configs(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Retrieve all API configurations with pagination via FastAPI proxy."""
    return await ProxyRequest.redirect("GET", f"{API_CONFIG_ENDPOINT}/", params={"limit": limit, "offset": offset})


@mcp.tool()
async def update_api_config(api_config_id: int, name: Optional[str] = None, endpoint: Optional[str] = None, method: Optional[str] = None, description: Optional[str] = None, headers: Optional[Dict[str, Any]] = None, body_template: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Update an existing API configuration via FastAPI proxy."""
    update_data = {k: v for k, v in locals().items() if v is not None and k != "api_config_id"}
    if not update_data:
        raise RuntimeError("No update data provided")
    model = ApiConfigUpdate(**update_data)
    return await ProxyRequest.redirect("PUT", f"{API_CONFIG_ENDPOINT}/{api_config_id}", model)


@mcp.tool()
async def delete_api_config(api_config_id: int) -> Dict[str, str]:
    """Delete an API configuration by ID via FastAPI proxy."""
    return await ProxyRequest.redirect("DELETE", f"{API_CONFIG_ENDPOINT}/{api_config_id}")


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
