# Contrato de Comunicación con el MCP Server

A2A y MCP no compiten, se complementan:

- **MCP** conecta a un agente con SUS herramientas/datos (agente ↔ herramienta).
- **A2A** conecta a un agente con OTRO agente (agente ↔ agente).

En este proyecto: el MCP Server del Equipo A da acceso a datos y herramientas, y A2A es lo que permite que agentes externos se comuniquen con ese sistema.

## Mecanismos para recibir actualizaciones de una tarea

- **Polling**: preguntar periódicamente con `GetTask`.
- **Streaming**: actualizaciones en tiempo real.
- **Push notifications**: el servidor avisa a un webhook cuando hay cambios.

Para el prototipo del viernes, **polling simple** es lo más realista de implementar a tiempo.

## Errores estándar a documentar

| Error | Código HTTP equivalente |
|---|---|
| Tarea no encontrada | 404 |
| Operación no soportada | 400 |
| Tipo de contenido no soportado | 400 |
| Error de autenticación | 401 |
| Error de autorización | 403 |
| Error de validación | 400 |
| Error del sistema | 500 |

---
*Fuente: especificación oficial de A2A — [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification)*
## Contrato verificado (12 de octubre de 2026)

Esta sección se actualizó con pruebas reales en el entorno contenerizado. Lo que no se probó está marcado como pendiente.

### Servicios y red

- Red de Docker compartida: `mcp-network` (tipo bridge); los contenedores se resuelven por nombre.
- Servicios: `auth-init` (genera llaves RS256 de prueba), `mcp-server` (puerto 8000), `agente_a` (puerto 8001), `agente_b` (reserva) e `integration-tests`.
- URL del servidor MCP desde la red de Docker: `http://mcp-server:8000/mcp`.
- La variable `MCP_SERVER_URL` se configura **sin** el sufijo `/mcp`, porque el código lo agrega (evita `/mcp/mcp`).

### Autenticación (dos tramos)

- Cliente → agente A2A: encabezado `Authorization: Bearer <API_KEY>`. Sin credenciales o con token inválido responde 401 (`{"detail":"Unauthorized access"}`).
- Agente A2A → servidor MCP: JWT firmado con RS256, con las declaraciones `iss` y `sub` = `agente_a`, `aud` = `mcp-interoperability-server`, `exp` = 3600 s y `scope` = `mcp:read mcp:tools` (el campo es `scope`, no `scopes`).
- Las credenciales no se versionan; se entregan por variables de entorno.

### Herramientas expuestas por el servidor MCP (verificadas con list_tools)

| Herramienta | Alcance requerido | Argumentos |
|---|---|---|
| `get_system_status` | `mcp:read` | ninguno |
| `echo` | `mcp:read` | `message` (texto) |
| `add` | `mcp:tools` | `a`, `b` (enteros) |

`calculator_service` y `system_service` son módulos internos del servidor, no herramientas: invocarlas por ese nombre devuelve `Unknown tool`.


### Endpoints del agente A2A

| Método | Ruta | Protección | Descripción |
|---|---|---|---|
| GET | `/.well-known/agent-card.json` | Pública (por diseño) | Tarjeta del agente (descubrimiento); declara `bearerAuth`. |
| POST | `/a2a/rpc` | Bearer | JSON-RPC 2.0, método `message/send`. Responde con la tarea en `TASK_STATE_SUBMITTED`. |
| GET | `/a2a/tasks/{task_id}` | Bearer | Consulta el estado y el resultado de una tarea (polling). |

### Estados de tarea

Formato en mayúsculas, homologado entre ambos equipos: `TASK_STATE_SUBMITTED`, `TASK_STATE_WORKING`, `TASK_STATE_INPUT_REQUIRED`, `TASK_STATE_AUTH_REQUIRED`, `TASK_STATE_COMPLETED`, `TASK_STATE_FAILED`, `TASK_STATE_CANCELED` y `TASK_STATE_REJECTED`.

La respuesta inmediata de `message/send` es `TASK_STATE_SUBMITTED`; la ejecución sigue en segundo plano. Si falla, la tarea queda en `TASK_STATE_FAILED` con el mensaje de error.

### Estado de las pruebas

| ID | Prueba | Resultado |
|---|---|---|
| P1 | Arranque coordinado de los servicios | Superada (8-oct) |
| P2 | Autenticación del cliente (200, tarea creada) | Superada (8 y 12-oct) |
| P3 | Rechazo con token inválido (401) | Superada (12-oct) |
| P4 | `list_tools` desde el agente | Superada (8-oct) |
| P5 | Invocación de `echo` desde el agente | Superada (8-oct) |
| P6 | Flujo extremo a extremo | Superada en 2.º intento (12-oct): tarea en `TASK_STATE_COMPLETED` usando `echo` |

El primer intento de P6 (8-oct) falló con `Unknown tool: 'calculator_service'`: el orquestador invocaba una herramienta que el servidor no expone.

### Pendientes

- Integrar en el repositorio común la corrección de `src/orchestrator.py` línea 35 (usar `echo`, o `add` con dos enteros).
- Decidir el mecanismo de credenciales entre el JWT firmado por el agente y el token de sesión propuesto por el Equipo A.
- Validar en el ambiente contenerizado del laboratorio con ambos equipos.
