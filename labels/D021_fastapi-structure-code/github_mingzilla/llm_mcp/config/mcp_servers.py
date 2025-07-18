"""
MCP Server Configuration

This file defines all available MCP servers and their configuration.
Adding a new MCP server requires only adding an entry here.
"""

import json
import os
from typing import Any, Dict

# Default MCP server configuration
MCP_SERVERS = {
    "api_config": {
        "url": "http://localhost:8000/mcp/",
        "description": "API Configuration Management",
        "tools": ["create_api_config", "get_api_config", "get_all_api_configs", "update_api_config", "delete_api_config"],
        "enabled": True,
        "port": 8000,
    },
    "calculator": {
        "url": "http://localhost:8010/mcp/",
        "description": "Mathematical Calculations",
        "tools": ["add", "multiply"],
        "enabled": True,
        "port": 8010,
    },
}


def load_mcp_server_config() -> Dict[str, Any]:
    """
    Load MCP server configuration.

    Priority order:
    1. Environment variable MCP_SERVERS_CONFIG (JSON string)
    2. Environment variable MCP_SERVERS_FILE (path to JSON file)
    3. Default configuration above

    Returns:
        Dictionary of MCP server configurations
    """
    # Check for environment variable override (JSON string)
    env_config = os.getenv("MCP_SERVERS_CONFIG")
    if env_config:
        try:
            custom_config = json.loads(env_config)
            print("Loaded MCP server config from MCP_SERVERS_CONFIG environment variable")
            return _apply_windows_ip_substitution(custom_config)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in MCP_SERVERS_CONFIG environment variable: {e}")

    # Check for configuration file override
    config_file = os.getenv("MCP_SERVERS_FILE")
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                print(f"Loaded MCP server config from file: {config_file}")
                return _apply_windows_ip_substitution(file_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load MCP server config file {config_file}: {e}")

    # Use default configuration
    print("Using default MCP server configuration")
    return _apply_windows_ip_substitution(MCP_SERVERS)


def _apply_windows_ip_substitution(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply Windows IP substitution for WSL environment compatibility.

    Args:
        config: MCP server configuration

    Returns:
        Configuration with URLs updated for Windows IP if needed
    """
    windows_ip = os.getenv("WINDOWS_IP")
    if not windows_ip:
        return config

    # Create a copy to avoid modifying the original
    updated_config = {}

    for server_name, server_config in config.items():
        updated_server_config = server_config.copy()

        # Replace localhost with Windows IP in URL
        if "url" in updated_server_config:
            url = updated_server_config["url"]
            if "localhost" in url or "127.0.0.1" in url:
                # Replace localhost/127.0.0.1 with Windows IP
                updated_url = url.replace("localhost", windows_ip).replace("127.0.0.1", windows_ip)
                updated_server_config["url"] = updated_url
                print(f"Updated {server_name} URL for Windows IP: {updated_url}")

        updated_config[server_name] = updated_server_config

    return updated_config


def load_enabled_mcp_servers() -> Dict[str, Any]:
    """
    Load and validate MCP server configuration, returning only enabled servers.

    This combines load_mcp_server_config(), validate_server_config(), and filtering
    of enabled servers into a single convenient function.

    Returns:
        Dictionary of enabled MCP server configurations

    Raises:
        ValueError: If configuration is invalid
    """
    # Load full configuration
    config = load_mcp_server_config()

    # Validate configuration
    validate_server_config(config)

    # Filter to only enabled servers
    enabled_servers = {server_name: server_config for server_name, server_config in config.items() if server_config.get("enabled", True)}

    print(f"Loaded {len(enabled_servers)} enabled servers: {list(enabled_servers.keys())}")
    return enabled_servers


def validate_server_config(config: Dict[str, Any]) -> bool:
    """
    Validate MCP server configuration.

    Args:
        config: MCP server configuration to validate

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If configuration is invalid
    """
    required_fields = ["url", "description"]

    for server_name, server_config in config.items():
        # Check required fields
        for field in required_fields:
            if field not in server_config:
                raise ValueError(f"Server '{server_name}' missing required field: {field}")

        # Validate URL format
        url = server_config["url"]
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"Server '{server_name}' has invalid URL format: {url}")

        # Validate tools list (if provided)
        tools = server_config.get("tools")
        if tools is not None and not isinstance(tools, list):
            raise ValueError(f"Server '{server_name}' tools must be a list")

        # Validate enabled flag
        enabled = server_config.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(f"Server '{server_name}' enabled flag must be boolean")

    return True
