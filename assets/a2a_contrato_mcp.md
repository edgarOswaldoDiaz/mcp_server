# Contrato de Comunicación con el MCP Server

A2A y MCP no compiten, se complementan:

- **MCP** conecta a un agente con SUS herramientas/datos (agente ↔ herramienta).
- **A2A** conecta a un agente con OTRO agente (agente ↔ agente), mediante mensajes y tareas.

En este proyecto: el MCP Server del Equipo A da acceso a datos y herramientas, y A2A es lo que permite que agentes externos se comuniquen con ese sistema.

## Mecanismos para recibir actualizaciones de una tarea

- **Polling**: preguntar periódicamente con `GetTask`.
- **Streaming**: actualizaciones en tiempo real.
- **Push notifications**: el servidor avisa a un webhook cuando hay cambios.

Para el prototipo del viernes, **polling simple** es lo más realista de implementar a tiempo.

## Errores estándar a documentar

| Error                          | Código HTTP equivalente |
| ------------------------------ | ----------------------- |
| Tarea no encontrada            | 404                     |
| Operación no soportada         | 400                     |
| Tipo de contenido no soportado | 400                     |
| Error de autenticación         | 401                     |
| Error de autorización          | 403                     |
| Error de validación            | 400                     |
| Error del sistema              | 500                     |

## Comunicación entre servicios

### API A2A

Los endpoints utilizados por el agente son:

| Operación                     | Método HTTP | Endpoint                       |
| ----------------------------- | ----------- | ------------------------------ |
| Consultar la ficha del agente | GET         | `/.well-known/agent-card.json` |
| Enviar un mensaje             | POST        | `/a2a/rpc`                     |
| Consultar una tarea           | GET         | `/a2a/tasks/{task_id}`         |

La API A2A utiliza mensajes JSON-RPC para las operaciones correspondientes.

### Servidor MCP

La URL utilizada entre contenedores es:

`http://mcp-server:8000/mcp`

Esta dirección utiliza el nombre del servicio `mcp-server` en la red de Docker.

El cliente MCP utiliza esta ruta para invocar herramientas del servidor.

## Herramientas MCP disponibles

El servidor MCP expone las siguientes herramientas verificadas:

| Herramienta         | Parámetros         | Función                              | Permiso requerido |
| ------------------- | ------------------ | ------------------------------------ | ----------------- |
| `get_system_status` | Ninguno            | Consulta el estado del servidor MCP. | `mcp:read`        |
| `echo`              | `message: str`     | Devuelve el mensaje recibido.        | `mcp:read`        |
| `add`               | `a: int`, `b: int` | Suma dos números enteros.            | `mcp:tools`       |

Los nombres y parámetros deben coincidir con los registrados en el servidor MCP. Una llamada a una herramienta que no esté registrada puede provocar un error de herramienta desconocida.

## Autenticación y autorización

El proyecto utiliza mecanismos de autenticación separados para las dos conexiones.

### Cliente → agente A2A

La API A2A requiere autenticación mediante el esquema Bearer en los endpoints protegidos.

Las pruebas E2E verifican que las solicitudes sin token, con token inválido o con un esquema de autorización distinto de Bearer sean rechazadas.

### Agente → servidor MCP

El cliente del agente genera un JWT firmado mediante **RS256**.

El token incluye los siguientes campos:

| Campo   | Valor o propósito                                                        |
| ------- | ------------------------------------------------------------------------ |
| `iss`   | `agente_a`, identifica al emisor.                                        |
| `sub`   | `agente_a`, identifica al sujeto del token.                              |
| `aud`   | `mcp-interoperability-server`, identifica la audiencia esperada.         |
| `exp`   | Tiempo de expiración; se calcula para una hora después de la generación. |
| `scope` | `mcp:read mcp:tools`, declara los permisos del token.                    |

El cliente firma el JWT con la clave privada configurada en `MCP_AUTH_PRIVATE_KEY_PATH`.

El servidor MCP carga la clave pública configurada en `MCP_AUTH_PUBLIC_KEY_PATH` y configura el verificador JWT con la audiencia indicada por `MCP_AUTH_AUDIENCE`.

Los permisos de cada herramienta se aplican mediante los scopes requeridos por su registro en el servidor MCP.

## Estados de una tarea A2A

Los siguientes estados están definidos en `src/schemas.py`:

| Estado                      | Significado                                                 |
| --------------------------- | ----------------------------------------------------------- |
| `TASK_STATE_SUBMITTED`      | La tarea fue recibida y registrada.                         |
| `TASK_STATE_WORKING`        | La tarea está en ejecución.                                 |
| `TASK_STATE_INPUT_REQUIRED` | La tarea requiere información adicional.                    |
| `TASK_STATE_AUTH_REQUIRED`  | La tarea requiere completar una condición de autenticación. |
| `TASK_STATE_COMPLETED`      | La tarea terminó correctamente.                             |
| `TASK_STATE_FAILED`         | La ejecución terminó con un error.                          |
| `TASK_STATE_CANCELED`       | La tarea fue cancelada.                                     |
| `TASK_STATE_REJECTED`       | La tarea fue rechazada.                                     |

En el flujo de ejecución actual, la tarea pasa de `TASK_STATE_SUBMITTED` a `TASK_STATE_WORKING` y termina en `TASK_STATE_COMPLETED` si la ejecución es satisfactoria, o en `TASK_STATE_FAILED` si ocurre una excepción.

La definición de un estado en el esquema no significa necesariamente que exista una prueba E2E específica para ese estado.

## Pruebas E2E relacionadas

Los siguientes archivos comprueban el comportamiento de la API A2A:

- `tests/e2e/test_conectividad.py`: ficha del agente, envío de mensajes, creación de tareas y polling.
- `tests/e2e/test_seguridad.py`: autenticación y errores JSON-RPC.

La ejecución satisfactoria del flujo completo también debe comprobar que la tarea llegue a `TASK_STATE_COMPLETED` y contenga el resultado esperado.

---

_Fuente: especificación oficial de A2A — [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification)_
