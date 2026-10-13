
"""
Genera el token JWT que utiliza el agente para autenticarse con MCP.
"""

import jwt
import time
import os


def create_agent_token() -> str:
    """Crea un JWT firmado con la clave privada del agente."""

    # La ruta puede configurarse mediante una variable de entorno.
    # Si no existe, se utiliza la ruta predeterminada.
    private_key_path = os.environ.get("MCP_AUTH_PRIVATE_KEY_PATH","/run/mcp-private/private_key.pem")

    # Carga la clave privada que se usará para firmar el token.
    with open(private_key_path, "r", encoding="utf-8") as f:
        private_key = f.read()

    # Datos que identifican al agente y definen la validez del token.
    payload = {
        "iss": "agente_a",  # Emisor del token.
        "sub": "agente_a",  # Identidad del agente.
        "aud": "mcp-interoperability-server",  # Servidor destinatario.
        "exp": int(time.time()) + 3600,  # Expira en una hora.
        "scope": "mcp:read mcp:tools"  # Permisos declarados.
    }

    # Firma el token con RS256 para que el servidor pueda verificarlo.
    return jwt.encode(payload, private_key, algorithm="RS256")
