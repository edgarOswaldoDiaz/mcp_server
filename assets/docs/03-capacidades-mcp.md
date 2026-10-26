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

## 2. Resources (Recursos de Lectura)
Puntos de enlace contextuales expuestos vía URIs:
* **`config://server`**: Expone la configuración activa del entorno en formato JSON.

## 3. Prompts (Plantillas de Contexto)
* **`system_diagnostic`**: Plantilla guiada para solicitar una inspección del estado y herramientas activas del servidor.