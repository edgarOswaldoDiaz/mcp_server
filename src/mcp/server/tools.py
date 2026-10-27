from fastmcp import FastMCP
from src.mcp.services.calculator_service import add_numbers
from src.mcp.services.system_service import get_system_status as get_system_status_service
from src.mcp.services.minio_service import MinIOService

def register_tools(mcp):
    
    @mcp.tool()
    def get_system_status() -> dict:
        """Returns the current status of the MCP server."""

        return get_system_status_service()

    @mcp.tool()
    def echo(message: str) -> dict:
        """Returns the received message."""

        return {
            "message": message
        }

    @mcp.tool()
    def add(a: int, b: int) -> dict:
        """Adds two integer numbers."""

        return add_numbers(a, b)
    
    # --- Herramientas de MinIO ---
    
    minio_service = MinIOService()

    @mcp.tool()
    def read_minio_json(object_key: str) -> dict:
        """Lee un archivo JSON desde el bucket configurado en MinIO."""
        return minio_service.read_json(object_key)

    @mcp.tool()
    def read_minio_parquet(object_key: str) -> str:
        """Lee un archivo Parquet desde MinIO y devuelve su contenido en formato JSON."""
        return minio_service.read_parquet(object_key)

    @mcp.tool()
    def read_minio_geoparquet(object_key: str) -> str:
        """Lee un archivo GeoParquet desde MinIO y devuelve su contenido en formato GeoJSON."""
        return minio_service.read_geoparquet(object_key)