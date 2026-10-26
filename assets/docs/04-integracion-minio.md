# 4. Integración Segura con MinIO

Se implementó el servicio `MinIOService` en `src/mcp/services/minio_service.py` para permitir que el servidor MCP lea datos almacenados en MinIO mediante la interfaz compatible con AWS S3.

## Principios de Implementación y Seguridad
1. **Desacoplamiento:** La lógica de lectura S3 con `boto3`, `pandas` y `geopandas` se encuentra aislada de la capa MCP.
2. **Uso de Usuarios Limitados:** Se evita el uso de la cuenta `root` de MinIO. El servicio consume credenciales inyectadas desde el entorno.
3. **Manejo de Errores y Excepciones:** Captura errores del SDK (`ClientError`) para gestionar accesos denegados (`AccessDenied`) y archivos no encontrados (`NoSuchKey`) en pruebas de seguridad.

## Variables de Entorno Requeridas (`docker-compose.yml`)
```yaml
environment:
  MINIO_ENDPOINT: http://minio:9000
  MINIO_ACCESS_KEY: mcp-reader-user
  MINIO_SECRET_KEY: tu_secret_key_limitada
  MINIO_BUCKET_NAME: nombre-del-bucket
  AWS_DEFAULT_REGION: us-east-1