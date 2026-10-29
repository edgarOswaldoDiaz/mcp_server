# Guía de pruebas: MCP + agente A2A + almacenamiento S3

Tres servicios, cada uno en su propia rama y su propio `docker-compose`. Ninguno necesita el código del otro:

| Servicio | Rama | Qué hace |
|---|---|---|
| Almacenamiento (RustFS; MinIO es equivalente) | `almacenamiento-rustfs` (MinIO: `Almacenamiento-MinIO`) | Guarda los datos sintéticos y aplica los permisos por bucket |
| Servidor MCP | `oauth-dpop-integracion` (PR #2) | Entrega herramientas de **solo lectura**; exige OAuth 2.0 + DPoP |
| Agente A2A | `arreglo-dpop-yahell` (PR #3) | Recibe tareas (`leer <ruta>`) y las ejecuta contra el MCP |

```
agente A2A --(OAuth 2.0 + DPoP)--> MCP --(cuenta lector-confidencial)--> RustFS / MinIO
```

Dos capas de solo lectura: el MCP solo expone herramientas de lectura, y el almacenamiento niega por política cualquier
escritura y cualquier lectura fuera de `datos-confidenciales`.

## Estado de verificación

- **Probado** (equipo de Brandon, Docker en WSL2): RustFS con las 9 piezas `init`, las 8 pruebas de permisos, carga de datos, MCP apuntando a RustFS, y el agente leyendo de punta a punta (`TASK_STATE_COMPLETED`).
- **Probado** con servicios simulados: `scripts/probar_agente.sh` (6 de 6).
- **No probado desde cero** en una máquina limpia: el orden completo de esta guía. Si algo falla, anota el paso y el mensaje.

## 0. Requisitos (una vez)

- Docker con Compose v2, y `git`.
- La red compartida entre servicios: `docker network create interoperability` (si ya existe, da un aviso y no pasa nada).
- Solo puede correr **un** almacenamiento a la vez: RustFS y MinIO usan el puerto 9000.

## 1. Almacenamiento (rama `almacenamiento-rustfs`)

```bash
cp rustfs/.env.example rustfs/.env       # edita y cambia TODOS los valores (12+ caracteres, letras y números)
docker compose -f rustfs/docker-compose.yml up -d
docker compose -f rustfs/docker-compose.yml --profile init up -d   # buckets, políticas y usuarios
docker compose -f rustfs/docker-compose.yml --profile init rm -f  # opcional: borra los contenedores init (quedan en Exited)
docker network connect interoperability rustfs                     # para que el MCP lo vea
```

Cargar datos y probar permisos (usa el contenedor del MCP, que ya trae `boto3`; hazlo después del paso 2):

```bash
docker network connect rustfs_red-datos mcp-server
docker exec -i --env-file rustfs/.env mcp-server python - < rustfs/cargar_datos.py
docker exec -i --env-file rustfs/.env mcp-server python - < rustfs/probar_permisos.py
```

Esperado: `RESULTADO: TODO CORRECTO` (8 casos `PASA`).

## 2. MCP (rama `oauth-dpop-integracion`)

En `deployment/compose/.env` (nunca se sube a git) define `MCP_JWT_SECRET`, `MCP_REFRESH_SECRET`, `MCP_AUTH_USERNAME`,
`MCP_AUTH_PASSWORD`, `MINIO_READER_USER=lector-confidencial` y `MINIO_READER_PASSWORD` (= `CONF_PASSWORD` de `rustfs/.env`).
Para RustFS añade `MINIO_ENDPOINT=http://rustfs:9000`.

```bash
docker volume create mcp-a2a-token        # el compose lo declara externo (resto de la versión anterior)
docker compose -f deployment/compose/docker-compose.yml up -d --build mcp-server
```

## 3. Agente (rama `arreglo-dpop-yahell`)

En `.env`: `MCP_USERNAME` y `MCP_PASSWORD` (los mismos `MCP_AUTH_*` del MCP).

```bash
docker compose up -d --build
```

## 4. Probar el agente (una sola orden)

```bash
./scripts/probar_agente.sh            # agente en http://localhost:8002
```

Esperado: 6 líneas `PASA` y `RESULTADO: TODO CORRECTO`.

## Si algo falla

| Síntoma | Causa probable |
|---|---|
| `FAILED` con `Login OAuth fallido` | `MCP_USERNAME` / `MCP_PASSWORD` del agente no coinciden con `MCP_AUTH_*` del MCP |
| `FAILED` con `Client failed to connect` | El MCP no está arriba o el agente no comparte red (`interoperability`) |
| `FAILED` con `AccessDenied` | Contraseña del lector en el MCP distinta de `CONF_PASSWORD`, o endpoint equivocado |
| `FAILED` con `no existe en el bucket` | Falta cargar datos (`cargar_datos.py`) |
| 401 al consultar el agente | Falta la cabecera `Authorization: Bearer <API_KEY>` del agente |
| El puerto 9000 está ocupado | Hay otro almacenamiento corriendo: apágalo con `docker stop` |
| `Permission denied` al cambiar de rama | Docker creó una carpeta como `root`: `sudo chown -R $USER:$USER <carpeta>` |

## Reglas de seguridad al trabajar

- **Nunca** `git add .` ni `git add -A`: agrega archivos por nombre. Los `.env` llevan contraseñas.
- **Nunca** `docker compose down -v` (borra los datos) ni `--remove-orphans` (borra contenedores de otros servicios).
- No pegues contraseñas ni tokens en chats, issues ni PRs.
