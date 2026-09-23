def registrar_herramientas(mcp):
    
    @mcp.tool()
    def sumar(a: int, b: int) -> int:
        """Suma dos números. Herramienta base para el Equipo A del INEGI."""
        return a + b
    
    @mcp.tool()
    def echo(mensaje: str) -> str:
        """Devuelve el mismo mensaje para pruebas de conexión."""
        return mensaje