# 1.2 Arquitectura MCP

## Descripción General
El Model Context Protocol (MCP) sigue un patrón de arquitectura cliente-servidor, donde un **Host MCP** (la aplicación de Inteligencia Artificial principal) establece y gestiona conexiones simultáneas con uno o más **Servidores MCP**. El host logra esta interacción instanciando un **Cliente MCP** dedicado para cada servidor con el que requiera comunicarse, manteniendo así un canal de comunicación independiente y estructurado.

El comportamiento y escalabilidad de las conexiones varía según el canal de comunicación:
*   **Servidores MCP locales:** Utilizan un mecanismo de transporte basado en `stdio` (entrada/salida estándar) y están diseñados comúnmente para dar servicio a un único cliente MCP.
*   **Servidores MCP remotos:** Utilizan un mecanismo de transporte basado en HTTP Streamable, lo que les permite atender y procesar peticiones provenientes de múltiples clientes MCP simultáneamente.

---

## Participantes Clave del Ecosistema
El funcionamiento del protocolo depende de la interacción armónica de tres componentes de software fundamentales:

*   **MCP Host:** Es la aplicación de IA central (como entornos de chat o asistentes de código) encargada de coordinar, inicializar y gestionar uno o varios clientes MCP de forma centralizada.
*   **Cliente MCP:** Es el componente de mediación interno que sostiene la conexión activa con un servidor específico. Se encarga de solicitar, recuperar y formatear el contexto proveniente del servidor para ponerlo a disposición del host.
*   **Servidor MCP:** Es el programa independiente encargado de exponer de forma segura los datos de contexto y las capacidades analíticas a los clientes que lo soliciten. 

> **Nota:** El término *Servidor MCP* califica estrictamente al programa que provee los datos de contexto, independientemente de la infraestructura donde resida. Estos componentes pueden ejecutarse de manera local (en la misma máquina del host) o de forma remota en la nube.

![Componentes Principales de la Arquitectura MCP](assets/arquitectura_mcp.png)

---

## Arquitectura de Capas
Conceptualmente, el protocolo MCP segmenta sus responsabilidades en dos capas estructurales, donde la capa de datos representa el núcleo interno y la capa de transporte actúa como la envoltura externa de comunicación:

1.  **Capa de Datos (Interna):** Define el protocolo de comunicación basado en el estándar `JSON-RPC 2.0`. Regula la gestión del ciclo de vida de las peticiones y define las primitivas esenciales del sistema, tales como la manipulación de herramientas, recursos, avisos y el envío de notificaciones.
2.  **Capa de Transporte (Externa):** Especifica los canales físicos e institucionales de comunicación que hacen posible el intercambio de bytes entre clientes y servidores. Administra el establecimiento de las conexiones según el medio, la estructuración de los mensajes en red y los flujos de autorización.

---

## Protocolo de la Capa de Datos y Mecanismos de Transporte

### Mensajería Basada en JSON-RPC 2.0
El intercambio formal de información utiliza **JSON-RPC 2.0** como su protocolo subyacente de llamada a procedimientos remotos. Bajo este esquema, tanto los clientes como los servidores tienen la facultad de enviarse solicitudes y emitir respuestas recíprocas. 

*   **Flujo Cliente a Servidor:** Los mensajes nativos del protocolo MCP se serializan al formato JSON-RPC, empaquetando diversas estructuras de datos junto con sus respectivas reglas de procesamiento para su envío seguro por la red.
*   **Flujo Servidor a Cliente:** Los flujos en formato JSON-RPC se reciben y se deserializan nuevamente en mensajes nativos interpretables por el protocolo MCP. Mientras que las solicitudes formales exigen una respuesta obligatoria del receptor, el protocolo admite el uso de **notificaciones**, las cuales se envían sin esperar ninguna confirmación o respuesta de retorno.

### Métodos de Transporte Principales
Para la transmisión física de las tramas JSON-RPC 2.0 entre la capa cliente y servidor, el protocolo implementa dos métodos de transporte principales adaptados al entorno físico de los recursos:

*   **Transporte Estándar I/O (stdio):** Diseñado específicamente para la integración de **recursos locales** (sistemas de archivos locales, bases de datos locales y APIs residentes en la misma máquina). Funciona mediante la transmisión directa y ligera de flujos de entrada y salida estándar, operando de manera sincrónica y optimizada para mensajería de baja latencia.
*   **Eventos Enviados por el Servidor (SSE - Server-Sent Events):** Orientado a la integración eficiente de **recursos remotos** (bases de datos en la nube o APIs externas de red). En este modelo, las solicitudes del cliente hacia el servidor se transmiten mediante peticiones estándar `HTTP POST`, mientras que el servidor utiliza el canal asíncrono `SSE` para enviar flujos de datos y eventos en tiempo real hacia el cliente, permitiendo gestionar múltiples llamadas concurrentes basadas en eventos.

![Diagrama Detallado de Flujos y Transportes en MCP](assets/model-context-protocol-architecture.jpg)

---

## Primitivas del Protocolo
Las primitivas constituyen los bloques de construcción esenciales de MCP; definen el catálogo de capacidades analíticas e informativas que los servidores pueden ofrecer y el rango de acciones que las aplicaciones de IA pueden ejecutar de forma autónoma. 

MCP clasifica las capacidades expuestas por los servidores en tres primitivas básicas:

*   **Herramientas (Tools):** Funciones ejecutables y procesables que los agentes de IA pueden invocar de manera dinámica para realizar alteraciones en el entorno (por ejemplo, escritura/lectura de archivos en disco, llamadas operativas a APIs externas o la ejecución de consultas y transacciones sobre bases de datos).
*   **Recursos (Resources):** Fuentes pasivas de información que proveen contexto puro a los modelos de lenguaje (como lecturas de archivos de texto, registros históricos extraídos de una base de datos o cargas de datos crudos de una API). Los recursos entregan datos con valor contextual, pero no ejecutan lógica de cálculo ni procesamiento activo.
*   **Instrucciones (Prompts):** Plantillas de comportamiento y flujos de trabajo predefinidos y reutilizables. Ayudan a estructurar y guiar la manera en que los modelos de lenguaje (LLMs) deben interactuar con el servidor y abordar tareas específicas.

Cada una de estas primitivas cuenta con métodos estándar expuestos en su ciclo de vida para controlar su **Descubrimiento** (`*/list`), su **Recuperación** (`*/get`) y su **Ejecución activa** (`tools/call`).

---

## Notificaciones
Para garantizar que los entornos se mantengan sincronizados y reactivos ante cambios en la infraestructura, el protocolo soporta el envío de notificaciones bidireccionales en tiempo real. 

*Ejemplo de uso:* Si un servidor MCP sufre una actualización dinámica en caliente (como la adición de una nueva herramienta analítica o la modificación estructural de una consulta en una base de datos), el servidor despacha de inmediato una notificación asíncrona en formato JSON-RPC 2.0 (sin requerir respuesta) para actualizar el catálogo de herramientas en todos los clientes que se encuentren conectados en ese instante.

---

## Referencias
>   Gutowska, A. (2026). Protocolo de contexto del modelo (MCP). *IBM*. https://www.ibm.com/mx-es/think/topics/model-context-protocol

>   Model Context Protocol. (s.f.). *What is the Model Context Protocol (MCP)?* https://modelcontextprotocol.io/docs/getting-started/intro
