# 09 - Autenticación OAuth 2.0 + DPoP

> Este documento **reemplaza** lo que los documentos 05 y 06 dicen sobre autenticación con llaves `.pem`
> y el servicio `token-init`. Ese esquema anterior (JWT firmado con RS256 leído de un volumen) ya no se usa.

## Qué cambió y por qué

Antes el agente mandaba un token **Bearer**: quien tuviera ese texto podía usarlo. Ahora el MCP exige
**OAuth 2.0 con DPoP** (RFC 9449): el token está ligado a una llave privada que solo conoce el cliente que lo
pidió, y en cada petición el cliente firma una prueba con esa llave. Un token copiado de un log o de la red
**no sirve** sin la llave. OAuth y Bearer no son excluyentes: OAuth es el protocolo para obtener tokens, y
DPoP es lo que hace que el token no sea un "pase al portador".

## Flujo

1. El agente genera un par de llaves ECDSA P-256 en memoria (la privada nunca sale del proceso).
2. `POST /oauth/token` con usuario y contraseña + cabecera `DPoP` (prueba firmada) → recibe un **access token**
   (10 min), un **refresh token** (7 días) y el scope `mcp:read`. Ambos quedan ligados a la llave (`cnf.jkt`).
3. Cada llamada a `/mcp` lleva `Authorization: DPoP <access_token>` y una cabecera `DPoP` con una prueba nueva.
4. Si el access token vence, el cliente llama a `POST /oauth/refresh` (también con prueba DPoP) y reintenta.
   Si la sesión estuvo inactiva más de 15 minutos, el refresh se rechaza y hay que hacer login de nuevo.

Un Bearer simple (`Authorization: Bearer ...`) se **rechaza** con 401.

## Qué valida el servidor

| Comprobación | Detalle |
|---|---|
| Prueba DPoP | tipo `dpop+jwt`, firma ES256 con la llave pública incluida, `htm` y `htu` iguales a la petición |
| Frescura | `iat` dentro de ±60 s |
| Sin reutilización | cada `jti` se acepta una sola vez (anti-replay) |
| Ligado al token | `ath` = hash del access token; `cnf.jkt` del token = huella de la llave que firmó la prueba |
| Permisos | scope `mcp:read` obligatorio |
| Inactividad | 15 min sin peticiones cierra la sesión |

Rutas: `POST /oauth/token`, `POST /oauth/refresh`, `/mcp` (protegida). `/docs`, `/redoc` y `/openapi.json` están cerradas.

## Variables de entorno (archivo `deployment/compose/.env`, no se sube a git)

Hay una plantilla en `deployment/compose/.env.example`.

| Variable | Para qué |
|---|---|
| `MCP_JWT_SECRET`, `MCP_REFRESH_SECRET` | firman los tokens (genera con `python3 -c "import secrets;print(secrets.token_urlsafe(48))"`) |
| `MCP_AUTH_USERNAME`, `MCP_AUTH_PASSWORD` | credenciales del agente |
| `MINIO_READER_USER`, `MINIO_READER_PASSWORD` | usuario **de solo lectura** del bucket confidencial (nunca el administrador) |
| `MINIO_BUCKET_NAME` | `datos-confidenciales` |
| `MCP_PUBLIC_BASE_URL` | URL con la que el agente llama al MCP (por defecto `http://mcp-server:8000`); **debe coincidir** o DPoP rechaza todo por `htu` |
| `MCP_IDLE_TIMEOUT_SECONDS`, `MCP_ACCESS_TTL_SECONDS` | opcionales (900 y 600) |

`MINIO_READER_PASSWORD` debe ser la misma que `CONF_PASSWORD` de `minio/.env` en la rama de almacenamiento.

## Solo lectura en dos capas

1. El MCP **no ofrece herramientas de escritura** (solo `read_minio_json`, `read_minio_parquet`, `read_minio_geoparquet`).
2. MinIO mismo rechaza escritura y acceso al otro bucket al usuario `lector-confidencial` (política
   `politica-confidencial`). Ver la rama `Almacenamiento-MinIO`.

## Cómo levantarlo y probarlo

    docker network create interoperability          # una sola vez
    docker compose -f deployment/compose/docker-compose.yml up -d --build mcp-server

Pruebas unitarias (18): `python -m pytest tests/unit -q`

Prueba de punta a punta con un agente de prueba, **dentro de la red de Docker** (DPoP valida la URL exacta):

    set -a; source deployment/compose/.env; set +a
    docker run --rm --network mcp_server_mcp-network -e MCP_BASE_URL=http://mcp-server:8000 \
      -e MCP_USERNAME="$MCP_AUTH_USERNAME" -e MCP_PASSWORD="$MCP_AUTH_PASSWORD" \
      mcp_server-mcp-server python scripts/e2e_agente.py

Debe terminar en `RESULTADO: TODO OK`. Para conectar el almacenamiento local se puede usar un archivo
`docker-compose.local.yml` propio (no versionado) que una el servicio a la red del almacenamiento.

## Limitaciones conocidas

- Las sesiones y los `jti` vistos viven **en memoria**: se pierden al reiniciar y no funcionan con varios workers.
- Los tokens se firman con HS256 (secreto compartido); no hay rotación de llaves ni de refresh token.
- No se usa el *nonce* de servidor de DPoP (el cliente lo soporta si algún día se añade).
- Hay un solo usuario de agente.
- `auth-init`, `token-init` e `integration-tests` del compose usan el esquema anterior y están obsoletos.
- El compose publica el puerto `8000:8000` en todas las interfaces; si el MCP solo lo usan contenedores, cámbialo a `127.0.0.1:8000:8000`.
