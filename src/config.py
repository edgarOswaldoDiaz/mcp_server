"""Configuración del agente A2A.

Los valores se leen de variables de entorno (o del archivo .env) con
pydantic-settings; si no existen, se usan los valores por defecto de aquí.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Parámetros de configuración del agente.

    Attributes:
        app_name: nombre del agente.
        api_key: token Bearer que deben presentar los clientes (primer tramo
            de autenticación). Se sobrescribe con la variable de entorno API_KEY.
        mcp_server_url: URL base del servidor MCP dentro de la red de Docker.
        mcp_timeout_seconds: espera máxima, en segundos, por llamada al MCP.
    """
    app_name: str = "A2A Agent Node"
    # Autenticación Cliente -> A2A
    api_key: str = "secret-a2a-token-123"
    # Autenticación A2A -> MCP 
    mcp_server_url: str = "http://mcp-server:8000"
    mcp_timeout_seconds: float = 10.0

    class Config:
        env_file = ".env"

settings = Settings()