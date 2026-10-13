
"""
Configura la verificación de tokens JWT en el servidor MCP.
"""

import os

from fastmcp.server.auth import JWTVerifier


def create_auth() -> JWTVerifier:
    """Crea el verificador JWT con la clave pública y la audiencia esperada."""

    # Obtiene la ruta de la clave pública desde la configuración.
    public_key_path = os.environ.get("MCP_AUTH_PUBLIC_KEY_PATH","/run/mcp-public/public_key.pem")

    # Define qué audiencia debe tener el token recibido.
    aud = os.environ.get("MCP_AUTH_AUDIENCE", "mcp-interoperability-server")

    # Carga la clave pública para comprobar las firmas de los tokens.
    with open(public_key_path, "r", encoding="utf-8") as file:
        public_key = file.read()

    # Devuelve el verificador que utiliza FastMCP.
    return JWTVerifier(public_key=public_key,audience=aud)
