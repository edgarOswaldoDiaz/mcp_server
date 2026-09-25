from fastmcp import Client
from .config import settings
from .mcp.client.auth_jwt import create_agent_token


class MCPService:
    """
    Cliente del servidor MCP.
    """
    def __init__(self):
        # el servidor sirve en "/mcp"
        self.mcp_url = f"{settings.mcp_server_url.rstrip('/')}/mcp"

    async def invoke_tool(self, tool_name: str, arguments: dict) -> dict:
        token = create_agent_token()
        async with Client(
            self.mcp_url,
            auth=token,              
            timeout=settings.mcp_timeout_seconds,
        ) as client:
            result = await client.call_tool(tool_name, arguments)
            return result.data

    async def fetch_resource(self, uri: str) -> dict:
        token = create_agent_token()
        async with Client(
            self.mcp_url,
            auth=token,
            timeout=settings.mcp_timeout_seconds,
        ) as client:
            result = await client.read_resource(uri) 
            return {"result": [c.text for c in result]}