import logging

from fastmcp import FastMCP
from src.mcp.services.calculator_service import add_numbers
from src.mcp.services.system_service import get_system_status as get_system_status_service
from src.mcp.services.minio_service import MinIOService
from src.mcp.services.object_key import InvalidObjectKey
from src.mcp.services.query_service import QueryService

logger = logging.getLogger(__name__)


def _ok(data: dict) -> dict:
    return {"ok": True, "data": data}


def _safe_call(callback, **kwargs) -> dict:
    try:
        return _ok(callback(**kwargs))
    except InvalidObjectKey as exc:
        return {"ok": False, "error": {
            "code": "INVALID_OBJECT_KEY",
            "message": str(exc),
        }}
    except Exception:
        logger.exception("Fallo al ejecutar una herramienta MCP")
        return {"ok": False, "error": {
            "code": "TOOL_ERROR",
            "message": "No se pudo completar la operación.",
        }}

def register_tools(mcp):
    
    @mcp.tool()
    def get_system_status() -> dict:
        """Devuelve el estado actual del servidor MCP."""

        return _safe_call(get_system_status_service)

    @mcp.tool()
    def echo(message: str) -> dict:
        """Devuelve el mensaje recibido."""

        return _ok({"message": message})

    @mcp.tool()
    def add(a: int, b: int) -> dict:
        """Suma dos números enteros."""

        return _ok(add_numbers(a, b))
    
    # --- Herramientas de almacenamiento y consulta ---
    
    minio_service = MinIOService()
    query_service = QueryService()

    @mcp.tool()
    def read_minio_json(object_key: str) -> dict:
        """Lee un archivo JSON desde el bucket configurado en MinIO."""
        return _safe_call(
            lambda object_key: {
                "object_key": object_key,
                "content": minio_service.read_json(object_key),
            },
            object_key=object_key,
        )

    @mcp.tool()
    def read_minio_parquet(object_key: str) -> dict:
        """Lee un archivo Parquet y devuelve sus filas en una salida estructurada."""
        return _safe_call(
            lambda object_key: {
                "object_key": object_key,
                "content": minio_service.read_parquet(object_key),
            },
            object_key=object_key,
        )

    @mcp.tool()
    def read_minio_geoparquet(object_key: str) -> dict:
        """Lee un archivo GeoParquet y devuelve su contenido GeoJSON estructurado."""
        return _safe_call(
            lambda object_key: {
                "object_key": object_key,
                "content": minio_service.read_geoparquet(object_key),
            },
            object_key=object_key,
        )

    @mcp.tool()
    def list_datasets() -> dict:
        """Lista datasets Parquet disponibles en el bucket confidencial."""
        return query_service.list_datasets()

    @mcp.tool()
    def describe_dataset(dataset_id: str) -> dict:
        """Devuelve las columnas y tipos de un dataset Parquet."""
        return query_service.describe_dataset(dataset_id)

    @mcp.tool()
    def query_dataset(dataset_id: str, sql: str) -> dict:
        """Ejecuta una consulta SELECT sobre el dataset indicado."""
        return query_service.query_dataset(dataset_id, sql)
