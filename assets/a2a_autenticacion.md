# Mecanismo de Autenticación A2A

El **Agent Card** declara, en un campo llamado `securitySchemes`, cómo debe autenticarse un cliente contra ese agente (se basa en el mismo modelo que usa OpenAPI 3).

## Tipos posibles (uno por esquema)

- API Key.
- HTTP estándar (Basic / Bearer).
- OAuth 2.0.
- OpenID Connect.
- mTLS (certificados de cliente y servidor).

El Agent Card también indica, en `securityRequirements`, cuál(es) de esos esquemas exige el agente antes de permitir el contacto.

## Manejo de fallas de autenticación

Si el token falta o no es válido, el servidor debe responder con un error de autenticación (equivalente a HTTP `401 Unauthorized`) y señalar qué esquema se necesita.

---
*Fuente: especificación oficial de A2A — [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification)*
