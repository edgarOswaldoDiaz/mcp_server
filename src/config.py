from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "A2A Agent Node"
    # Autenticación Cliente -> A2A
    api_key: str = "secret-a2a-token-123"
    # Autenticación A2A -> MCP 
    mcp_server_url: str = "http://mcp-server:8000"
    mcp_timeout_seconds: float = 10.0

    class Config:
        env_file = ".env"

settings = Settings()
