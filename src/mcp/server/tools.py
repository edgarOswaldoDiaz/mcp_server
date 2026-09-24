from src.mcp.services.system_service import get_system_status as get_system_status_service

def registrar_herramientas(mcp):
    
    @mcp.tool()
    def sumar(a: int, b: int) -> int:
        """Suma dos números. Herramienta base para el Equipo A del INEGI."""
        return a + b
    
    @mcp.tool()
    def echo(mensaje: str) -> str:
        """Devuelve el mismo mensaje para pruebas de conexión."""
        return mensaje

    @mcp.tool()
    def get_system_status() -> dict:
        """Returns the current status of the MCP server."""

        return get_system_status_service()