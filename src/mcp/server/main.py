from fastmcp import FastMCP
from src.mcp.server.tools import registrar_herramientas
from src.mcp.server.prompts import register_prompts
from src.mcp.server.resources import register_resources

mcp = FastMCP("Servidor_INEGI_EquipoA")
registrar_herramientas(mcp)
register_resources(mcp)
register_prompts(mcp)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)