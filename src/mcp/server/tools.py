from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes

from src.mcp.services.calculator_service import add_numbers
from src.mcp.services.system_service import get_system_status as get_system_status_service

def register_tools(mcp):
    
    @mcp.tool(auth=require_scopes("mcp:read"))
    def get_system_status() -> dict:
        """Returns the current status of the MCP server."""

        return get_system_status_service()

    @mcp.tool(auth=require_scopes("mcp:read"))
    def echo(message: str) -> dict:
        """Returns the received message."""

        return {
            "message": message
        }

    @mcp.tool(auth=require_scopes("mcp:tools"))
    def add(a: int, b: int) -> dict:
        """Adds two integer numbers."""

        return add_numbers(a, b)