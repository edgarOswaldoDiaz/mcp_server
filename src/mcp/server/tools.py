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
    
    # --- Herramientas de MinIO ---
    minio_service = MinIOService()

    @mcp.tool()
    def read_minio_json(object_key: str) -> str:
        """Lee un archivo JSON desde el bucket configurado en MinIO."""
        import json
        
        try:
            # Llamamos al servicio actual
            datos = minio_service.read_json(object_key)
            # MCP prefiere recibir strings de texto limpios formateados
            return json.dumps(datos, indent=2, ensure_ascii=False)
            
        except (FileNotFoundError, PermissionError, RuntimeError) as e:
            # Capturamos errores controlados y los devolvemos como texto legible
            return f"Error al leer MinIO: {str(e)}"
        except Exception as e:
            # Atrapamos cualquier otro error inesperado para evitar caídas del servidor
            return f"Error inesperado: {str(e)}"

    @mcp.tool()
    def read_minio_parquet(object_key: str) -> str:
        """Lee un archivo Parquet desde MinIO y devuelve su contenido."""
        try:
            return minio_service.read_parquet(object_key)
        except Exception as e:
            return f"Error al leer Parquet en MinIO: {str(e)}"

    @mcp.tool()
    def read_minio_geoparquet(object_key: str) -> str:
        """Lee un archivo GeoParquet desde MinIO y devuelve su contenido."""
        try:
            return minio_service.read_geoparquet(object_key)
        except Exception as e:
            return f"Error al leer GeoParquet en MinIO: {str(e)}"