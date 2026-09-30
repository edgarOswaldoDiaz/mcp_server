import json

from fastmcp import FastMCP

from src.mcp.server.metadata import (
    SERVER_NAME,
    SERVER_VERSION,
)


def register_resources(mcp: FastMCP) -> None:
    """Register all MCP resources."""

    @mcp.resource("config://server")
    def get_server_config() -> str:
        """Returns the MCP server configuration."""

        config = {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "environment": "development",
        }

        return json.dumps(config, indent=2)