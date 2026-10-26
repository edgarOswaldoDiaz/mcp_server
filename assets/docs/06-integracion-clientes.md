# 6. Integración con Agente de Inteligencia Artificial (A2A)

Este documento describe la comunicación entre el **Servidor MCP** y un **Agente de Inteligencia Artificial**, desplegados en **contenedores Docker independientes** que se conectan mediante una **red Docker externa compartida** usando el transporte **HTTP/SSE**.

---

## 1. Arquitectura de Red entre Contenedores

Para permitir la comunicación entre contenedores separados en diferentes pilas de Docker, ambos se vinculan a una red externa declarada previamente en el sistema host.

### Creación de la Red Externa (Ejecutar en Host):
```bash
docker network create mcp-interop-network
```

### Configuración en el `docker-compose.yml` de cada contenedor:
```yaml
networks:
  mcp-interop-network:
    external: true
```

---

## 2. Parámetros de Conexión

El Agente de IA invoca las herramientas consumiendo los siguientes puntos de enlace:

* **URL en Red Externa (Agente -> MCP):** `http://mcp-server:8000/mcp`
* **Protocolo:** HTTP / SSE (JSON-RPC 2.0)
* **Encabezado de Autenticación:**
  ```text
  Authorization: Bearer <TOKEN_JWT>
  ```
  *(Requiere permisos `mcp:read` y `mcp:tools`)*

---

## 3. Herramientas Disponibles

El servidor expone el siguiente catálogo para el Agente de IA:

* **`get_system_status`**: Estado de salud y versión del servidor MCP.
* **`echo`**: Prueba de conectividad y latencia entre contenedores.
* **`add`**: Operaciones de cálculo básico.
* **`read_minio_json`**: Lectura y estructuración de archivos `.json` en MinIO.
* **`read_minio_parquet`**: Procesamiento de datos tabulares `.parquet` en MinIO.
* **`read_minio_geoparquet`**: Lectura de capas geoespaciales `.geoparquet` a GeoJSON.

---

## 4. Prueba de Interconexión desde el Contenedor del Agente

Para validar que el contenedor del Agente de IA alcanza al contenedor del servidor MCP a través de la red externa:

```bash
docker exec -it contenedor-agente curl -X POST http://mcp-server:8000/mcp \
     -H "Authorization: Bearer <TOKEN_JWT>" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```