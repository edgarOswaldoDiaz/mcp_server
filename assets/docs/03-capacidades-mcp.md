# 3. Capacidades MCP Implementadas

El servidor expone las primitivas estándar definidas en la especificación MCP a través del framework `FastMCP`:

## 1. Tools (Herramientas Ejecutables)
Funciones que los modelos de lenguaje pueden invocar dinámicamente:
* **`get_system_status`**: Devuelve el estado de salud y versión del servidor MCP.
* **`echo`**: Retorna el mensaje recibido para pruebas de latencia y conectividad.
* **`add`**: Suma de números enteros mediante la capa `calculator_service`.
* **`read_minio_json`**: Lee y deserializa archivos `.json` desde un bucket de MinIO.
* **`read_minio_parquet`**: Lee tablas en formato `.parquet` y las expone estructuradas en JSON.
* **`read_minio_geoparquet`**: Lee capas de información geográfica en formato GeoParquet y las devuelve como GeoJSON.

### Herramientas SQL de solo lectura

El servidor expone tres herramientas para consultar archivos Parquet del bucket configurado (por defecto, `datos-confidenciales`):

* **`list_datasets`**: enumera los objetos `.parquet` y devuelve `dataset_id`, formato y tamaño.
* **`describe_dataset(dataset_id)`**: devuelve el esquema con nombres de columnas y tipos.
* **`query_dataset(dataset_id, sql)`**: ejecuta una sentencia `SELECT` sobre la tabla lógica `dataset` y devuelve columnas, filas, cantidad de filas y si el resultado fue truncado.

Todas las herramientas usan el sobre `{"ok": true, "data": {...}}` o `{"ok": false, "error": {"code": "...", "message": "..."}}`. Los identificadores de herramientas y campos están en inglés; esta documentación y los comentarios del código están en español.

El servidor resuelve `dataset_id` como una clave del bucket configurado. DuckDB recibe los datos como una tabla registrada en memoria, tiene deshabilitado el acceso externo y no puede abrir otras rutas. La consulta debe usar `dataset` como fuente y queda limitada por `QUERY_MAX_ROWS` (500 por defecto), `QUERY_TIMEOUT_SECONDS` (10 segundos) y `QUERY_MAX_FILE_BYTES` (256 MiB). Las credenciales S3 deben pertenecer al usuario de lectura del bucket confidencial.

## 2. Resources (Recursos de Lectura)
Puntos de enlace contextuales expuestos vía URIs:
* **`config://server`**: Expone la configuración activa del entorno en formato JSON.

## 3. Prompts (Plantillas de Contexto)
* **`system_diagnostic`**: Plantilla guiada para solicitar una inspección del estado y herramientas activas del servidor.
