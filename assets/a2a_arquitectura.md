# Arquitectura y Roles del Protocolo A2A

A2A es un estándar abierto (iniciado por Google y donado a la Linux Foundation) que permite que agentes de IA independientes, construidos en frameworks distintos, se comuniquen entre sí sin necesidad de conocer los detalles internos de cada uno.

## Roles

- **A2A Client**: el agente que inicia la solicitud.
- **A2A Server / Remote Agent**: el agente que recibe la solicitud y la procesa.

## Agent Card

Es un documento JSON público que cada agente expone (normalmente en `/.well-known/agent-card.json`) con su identidad, capacidades, habilidades (*skills*), formas de comunicación soportadas y requisitos de autenticación. Así es como un agente descubre qué puede hacer otro antes de contactarlo.

## Metas clave

- **Interoperabilidad**: conectar sistemas de agentes distintos entre sí.
- **Colaboración**: permitir que los agentes deleguen tareas y compartan contexto.
- **Descubrimiento**: que un agente encuentre y entienda las capacidades de otro dinámicamente.
- **Flexibilidad**: soporta respuesta directa, streaming en tiempo real o notificaciones asíncronas.
- **Seguridad de nivel empresarial**.
- **Soporte nativo para tareas de larga duración** (asincronía).

## Principios de diseño

- **Simple**: reutiliza estándares existentes (HTTP, JSON-RPC 2.0, Server-Sent Events) en vez de inventar algo nuevo.
- **Listo para empresa**: contempla autenticación, monitoreo y trazabilidad.
- **Pensado primero para lo asíncrono**: diseñado para tareas que pueden tardar mucho, incluyendo interacción humana en el proceso.
- **Agnóstico de modalidad**: soporta texto, archivos y datos estructurados.
- **Ejecución opaca**: los agentes colaboran según lo que declaran públicamente, sin exponer su lógica interna, memoria o herramientas.

---
*Fuente: especificación oficial de A2A — [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification)*
