# MinIO para datos confidenciales sintéticos

Simula un entorno de datos confidenciales con almacenamiento S3 (MinIO), usuarios limitados y datos sintéticos (Parquet, GeoParquet y JSON). Todos los datos son inventados.

## Contenido

- `docker-compose.yml`: MinIO con imagen fijada por digest, puertos solo en 127.0.0.1, red `red-datos` y volumen `minio_datos`.
- `.env.example`: plantilla de variables. Se copia a `.env`, que no se sube a Git.
- `scripts/`: pruebas en Python (boto3).
- `politicas/`: políticas JSON de solo lectura, una por bucket.

## Requisitos

Docker con Compose y Python 3 con venv. Todos los comandos se corren desde la raíz del repositorio.

## 1. Configurar y levantar

    cp minio/.env.example minio/.env
    nano minio/.env
    docker compose -f minio/docker-compose.yml up -d

En `.env` pon un usuario y una contraseña propios: solo letras y números, 12 o más caracteres. No uses `minioadmin`.
API: http://127.0.0.1:9000 y consola web: http://127.0.0.1:9001

## 2. Cargar variables y preparar el cliente mc

    set -a; source minio/.env; set +a
    export MC_HOST_local="http://$MINIO_ROOT_USER:$MINIO_ROOT_PASSWORD@minio:9000"
    MC="docker run --rm --network minio_red-datos -e MC_HOST_local -v $PWD/minio/politicas:/politicas:ro cgr.dev/chainguard/minio-client:latest"

## 3. Entorno de Python y datos de prueba

    python3 -m venv ~/venv-minio
    source ~/venv-minio/bin/activate
    pip install pandas pyarrow boto3 geopandas
    export REPO="$PWD"
    mkdir -p ~/minio-prueba && cd ~/minio-prueba
    python "$REPO/minio/scripts/generar_parquet.py"
    python "$REPO/minio/scripts/subir_parquet.py"
    python "$REPO/minio/scripts/leer_parquet.py"
    python "$REPO/minio/scripts/geoparquet.py"
    python "$REPO/minio/scripts/json_prueba.py"

## 4. Bucket público, políticas y usuarios limitados (automático)

En `minio/.env` agrega `LECTOR_PASSWORD` y `CONF_PASSWORD` (ver `.env.example`). Luego:

    docker compose -f minio/docker-compose.yml --profile init up -d
    docker compose -f minio/docker-compose.yml --profile init ps -a

Cada comando de `mc` es un servicio aparte (la imagen de `mc` no trae shell), encadenados:
`mc-listo` → buckets → políticas → usuarios → asignación de políticas. Todos deben terminar en `Exited (0)`.
Si uno falla, mira `docker compose -f minio/docker-compose.yml --profile init logs <servicio>`.
No corren con un `up` normal; solo con `--profile init`.

Las contraseñas de los usuarios deben ser de 12 o más caracteres, solo letras y números, y distintas entre sí.

## 5. Prueba de permisos

    python "$REPO/minio/scripts/prueba_lector.py"
    python "$REPO/minio/scripts/prueba_cruzada.py"

Resultado esperado: `lector-publico` solo lee `datos-publicos`. `lector-confidencial` solo lee `datos-confidenciales`. Ninguno puede escribir. Todo lo demás debe salir RECHAZADO (AccessDenied).

## Apagar

- `docker compose -f minio/docker-compose.yml down` apaga y conserva los datos.
- `docker compose -f minio/docker-compose.yml down -v` apaga y borra los datos.

## Advertencias

- Las credenciales de administrador (root) son solo para administrar. Los agentes y el MCP deben usar usuarios limitados.
- Nunca subas `.env` ni pegues contraseñas en capturas o chats de grupo.
- Mientras corre `mc`, `MC_HOST_local` contiene la contraseña de administrador y se ve con `docker inspect`. Usa contenedores efímeros (`--rm`).

## No probado todavía

- Conexión del MCP y de los agentes con usuarios limitados.
- Separación de redes dentro del compose del equipo (el MCP en ambas redes y MinIO solo en la de datos).
- HTTPS y auditoría de accesos.
- El compose de Equipo A espera el host `minio` y el bucket `mcp-bucket`, y estas pruebas usan `datos-confidenciales`. Falta alinear nombres.
