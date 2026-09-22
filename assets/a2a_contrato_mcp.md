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
