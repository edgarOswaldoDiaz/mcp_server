# Esquema de Mensajes A2A

## Task

Es la unidad central de trabajo. Sus campos principales:

- `id`: identificador único de la tarea.
- `contextId`: agrupa varias tareas que pertenecen a la misma conversación.
- `status`: estado actual + mensaje asociado.
- `artifacts`: resultados producidos por la tarea.
- `history`: mensajes previos de esa tarea.

### Ciclo de vida de una Task

`submitted` → `working` → (puede pausarse en `input-required` o `auth-required` si falta información o autenticación) → termina en uno de estos 4 estados finales: `completed`, `failed`, `canceled` o `rejected`.

## Message

Es una "vuelta" de comunicación entre cliente y agente. Campos:

- `messageId`: identificador único del mensaje.
- `contextId` (opcional).
- `taskId` (opcional).
- `role`: quién envía el mensaje (`user` o `agent`).
- `parts`: el contenido real del mensaje.
- `metadata` (opcional).

## Part

Es la pieza más pequeña de contenido dentro de un mensaje. Puede ser una de estas cuatro (solo una a la vez):

- `text`: texto plano.
- `raw`: archivo en bytes.
- `url`: URL apuntando a un archivo.
- `data`: datos estructurados (JSON).

## Artifact

Es el resultado final que el agente entrega al terminar una tarea. Campos: `artifactId`, `name`, `description`, `parts`.

## Transporte

JSON-RPC 2.0 sobre HTTPS. El método para enviar un mensaje se llama `message/send`.

### Ejemplo de mensaje

```json
// Solicitud (cliente → agente)
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "message/send",
  "params": {
    "message": {
      "messageId": "msg-001",
      "role": "user",
      "parts": [{ "text": "Consulta el dataset del censo 2025" }]
    }
  }
}

// Respuesta (el agente crea una Task)
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": "task-789",
    "contextId": "ctx-123",
    "status": { "state": "TASK_STATE_WORKING", "timestamp": "2026-09-22T10:00:00Z" }
  }
}
```

---
*Fuente: especificación oficial de A2A — [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification)*
