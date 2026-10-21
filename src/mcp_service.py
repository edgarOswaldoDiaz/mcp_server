"""Servicio de integración con el servidor MCP a través de mcp-network.

Lee la llave/token generada por el Equipo A directamente desde un volumen montado
en Docker y la envía en las peticiones al servidor MCP.
"""

import os
from fastmcp import Client
from .config import settings


class MCPService:
    """Cliente para la interacción con el servidor MCP."""

    def __init__(self):
        self.mcp_url = f"{settings.mcp_server_url.rstrip('/')}/mcp"

    def _read_token_from_volume(self) -> str:
        """Lee la llave/token provista por el Equipo A en el volumen de Docker.

        Raises:
            FileNotFoundError: Si el archivo con la llave no existe en la ruta configurada.
        """
        token_path = settings.mcp_token_path
        if not os.path.exists(token_path):
            raise FileNotFoundError(
                f"No se encontró la llave/token del Equipo A en el volumen montado: {token_path}"
            )
        
        with open(token_path, "r", encoding="utf-8") as f:
            token = f.read().strip()
        
        return token

    async def invoke_tool(self, tool_name: str, arguments: dict) -> dict:
        """Invoca una herramienta en el servidor MCP mediante la red interna mcp-network."""
        token = self._read_token_from_volume()
        async with Client(
            self.mcp_url,
            auth=token,              
            timeout=settings.mcp_timeout_seconds,
        ) as client:
            result = await client.call_tool(tool_name, arguments)
            return result.data

    async def fetch_resource(self, uri: str) -> dict:
        """Recupera un recurso del servidor MCP mediante la red interna mcp-network."""
        token = self._read_token_from_volume()
        async with Client(
            self.mcp_url,
            auth=token,
            timeout=settings.mcp_timeout_seconds,
        ) as client:
            result = await client.read_resource(uri) 
            return {"result": [c.text for c in result]}
