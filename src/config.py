"""Configuración del agente A2A (Equipo B).

Los valores se leen de variables de entorno o de un archivo .env usando pydantic-settings.
Incluye la ruta al volumen en Docker donde el Equipo A deposita las llaves/tokens.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Parámetros de configuración del agente.

    Attributes:
        app_name: Nombre del agente A2A.
        api_key: Token Bearer que deben presentar los clientes al autenticarse.
        mcp_server_url: URL base del servidor MCP en la red interna mcp-network.
        mcp_timeout_seconds: Espera máxima en segundos para respuestas del MCP.
        mcp_token_path: Ruta en el volumen montado de Docker donde el Equipo A deposita el token/llave.
    """
    app_name: str = "A2A Agent Node"
    # Autenticación Cliente -> A2A (Equipo B)
    api_key: str = "secret-a2a-token-123"
    
    # Red interna Docker (mcp-network)
    mcp_server_url: str = "http://mcp-server:8000"
    mcp_timeout_seconds: float = 10.0
    
    # Ruta de lectura del volumen montado del Equipo A (ReadOnly)
    mcp_token_path: str = "/run/mcp-token/access_token.jwt"

    class Config:
        env_file = ".env"

settings = Settings()
