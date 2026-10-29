"""Servicio de integración con el servidor MCP con OAuth 2.0 + DPoP (RFC 9449).

Misma clase y mismos métodos que antes (DPoPClientService.invoke_tool / fetch_resource), pero
ahora la autenticación la hace DPoPAuth (ver dpop_auth.py):
  - hace login en POST /oauth/token con usuario y contraseña (del entorno) y una prueba DPoP;
  - en CADA petición manda  Authorization: DPoP <token>  +  la cabecera DPoP firmada (ES256);
  - renueva el token solo si el MCP responde 401.
Ya no se lee ningún token de un volumen ni se manda un Bearer simple.
"""

import os

from fastmcp import Client

from .dpop_auth import DPoPAuth

_AUTH = None  # una sola llave y sesión por proceso: no se vuelve a loguear en cada llamada


def _get_auth(base_url: str) -> DPoPAuth:
    global _AUTH
    if _AUTH is None:
        user = os.environ.get("MCP_USERNAME")
        password = os.environ.get("MCP_PASSWORD")
        if not user or not password:
            raise RuntimeError("Faltan MCP_USERNAME y MCP_PASSWORD en el entorno (.env)")
        _AUTH = DPoPAuth(base_url, user, password)
    return _AUTH


class DPoPClientService:
    def __init__(self):
        self.base_url = os.environ.get("MCP_SERVER_URL", "http://mcp-server:8000").rstrip("/")
        self.mcp_url = f"{self.base_url}/mcp"
        self.timeout = float(os.environ.get("MCP_TIMEOUT_SECONDS", 10.0))

    async def invoke_tool(self, tool_name: str, arguments: dict) -> dict:
        async with Client(self.mcp_url, auth=_get_auth(self.base_url), timeout=self.timeout) as client:
            result = await client.call_tool(tool_name, arguments)
            return result.data

    async def fetch_resource(self, uri: str) -> dict:
        async with Client(self.mcp_url, auth=_get_auth(self.base_url), timeout=self.timeout) as client:
            result = await client.read_resource(uri)
            return {"result": [c.text for c in result]}
