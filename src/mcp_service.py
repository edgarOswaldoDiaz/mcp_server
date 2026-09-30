from fastmcp import Client

from .config import settings
from .mcp.client.auth_jwt import create_agent_token


class MCPService:
    """
    Cliente real del servidor MCP (protocolo Streamable HTTP + JWT).

    Reemplaza tanto la version REST simplificada original como la version
    con mcp.client.sse.sse_client (transporte viejo, no coincide con el
    servidor real que corre transport="streamable-http").
    """

    def __init__(self):
        # el servidor real sirve en "/mcp", no en la raiz ni en "/sse"
        self.mcp_url = f"{settings.mcp_server_url.rstrip('/')}/mcp"

    async def invoke_tool(self, tool_name: str, arguments: dict) -> dict:
        token = create_agent_token()
        async with Client(
            self.mcp_url,
            auth=token,                     # string -> Bearer automatico; NO usar headers=
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
            result = await client.read_resource(uri)  # ya es una lista, sin .contents
            return {"result": [c.text for c in result]}