from fastmcp import FastMCP
from src.mcp.server.tools import registrar_herramientas
mcp = FastMCP("Servidor_INEGI_EquipoA")
registrar_herramientas(mcp)

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)