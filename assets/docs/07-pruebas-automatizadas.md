# 7. Pruebas Automatizadas (Pytest en Contenedor)

Este documento describe la ejecución de las pruebas unitarias e integración del **Servidor MCP** ejecutadas de forma aislada mediante un contenedor Docker dedicado.

---

## 1. Ejecución de la Suite de Pruebas

Para validar el funcionamiento del servidor y sus servicios (`calculator`, `system`, `minio`), ejecuta el contenedor de pruebas desde la carpeta de composición:

```bash
# Navegar a la carpeta de despliegue
cd deployment/compose

# Ejecutar la suite completa en contenedor aislado
docker compose --profile test run --rm integration-tests
```

---

## 2. Tipos de Pruebas Incluidas

1. **Pruebas Unitarias (`tests/unit`):** Valida la lógica de negocio interna y la correcta inicialización del cliente de MinIO.
2. **Pruebas de Integración (`tests/integration`):** Comprueba que el transporte MCP (HTTP/SSE) y las herramientas registradas respondan de acuerdo con la especificación.

---

## 3. Verificación de Invocación desde Contenedor

Puedes verificar que las herramientas del servidor responden correctamente invocando una prueba rápida dentro del contenedor activo:

```bash
docker exec -it mcp-server python3 -c "from src.mcp.services.minio_service import MinIOService; print('Servicios listos')"
```