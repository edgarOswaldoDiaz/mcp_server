# 5. Despliegue y Orquestación en Contenedores (Docker)

Dado que la arquitectura del proyecto está completamente contenerizada, no es necesario realizar instalaciones manuales de entornos virtuales o librerías en el sistema operativo host. Todo el servidor MCP, sus dependencias de datos (`boto3`, `pandas`, `geopandas`) y los servicios de soporte corren dentro de contenedores aislados.

---

## 1. Estructura de Despliegue (`docker-compose.yml`)

El archivo de orquestación ubicado en `deployment/compose/docker-compose.yml` gestiona el ciclo de vida del servidor MCP, la inyección segura de variables de entorno y los volúmenes de red.

### Fragmento clave del servicio `mcp-server`:

```yaml
    mcp-server:
      build:
        context: ../..
        dockerfile: deployment/docker/Dockerfile.mcp
      container_name: mcp-server
      ports:
        - "8000:8000"
      environment:
        - MCP_HOST=0.0.0.0
        - MCP_PORT=8000
        - MINIO_ENDPOINT=http://minio:9000
        - MINIO_ACCESS_KEY=mcp-reader-user
        - MINIO_SECRET_KEY=tu_secret_key_limitada
        - MINIO_BUCKET_NAME=nombre-del-bucket
        - AWS_DEFAULT_REGION=us-east-1
      networks:
        - mcp-network
        - interoperability
```

---

## 2. Comandos para Levantar el Contenedor

Para construir la imagen de Docker con las nuevas dependencias e iniciar el servicio en segundo plano, ejecuta los siguientes comandos desde tu terminal (en el directorio del proyecto):

```bash
# 1. Navegar a la carpeta de composición
cd deployment/compose

# 2. Construir y levantar el contenedor del servidor MCP
docker compose up -d --build mcp-server
```

---

## 3. Verificación del Contenedor en Ejecución

1. **Revisar el estado de los contenedores:**
   ```bash
   docker compose ps
   ```

2. **Monitorear los logs en tiempo real para confirmar que FastMCP cargó las herramientas:**
   ```bash
   docker logs -f mcp-server
   ```

3. **Verificar que las variables de entorno de MinIO se cargaron correctamente dentro del contenedor:**
   ```bash
   docker exec mcp-server env | grep MINIO
   ```