from fastmcp import FastMCP

from src.mcp.server.metadata import (
    SERVER_DESCRIPTION,
    SERVER_NAME,
)
from src.mcp.server.prompts import register_prompts
from src.mcp.server.resources import register_resources
from src.mcp.server.tools import register_tools
from src.mcp.server.auth import create_auth


def create_server(use_auth: bool = True) -> FastMCP:
    auth = create_auth() if use_auth else None

    mcp = FastMCP(
        name=SERVER_NAME,
        instructions=SERVER_DESCRIPTION,
        auth=auth,
    )

    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)

    return mcp


if __name__ == "__main__":
    mcp = create_server()
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )