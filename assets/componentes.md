# 1.3 Componentes y Características del Ecosistema MCP

## Arquitectura de Componentes del Ecosistema

El ecosistema de *Model Context Protocol* (MCP) opera mediante la interacción lógica de componentes definidos que dividen las responsabilidades de control, mediación y aprovisionamiento de capacidades.

### 1. Host (Proceso Coordinador)

El proceso *Host* actúa como el contenedor principal y el orquestador del entorno de ejecución. Es la aplicación con la que interactúa la persona usuaria (por ejemplo, Claude.ai o un IDE), y coordina múltiples clientes al mismo tiempo. Sus responsabilidades clave incluyen:

* **Gestión de Instancias:** Crea y administra de forma centralizada múltiples instancias de clientes.
* **Ciclo de Vida y Conexiones:** Controla los permisos de conexión y el ciclo de vida de cada cliente acoplado.
* **Políticas de Seguridad:** Ejecuta y hace cumplir las políticas de seguridad institucional junto con los requerimientos de consentimiento del usuario.
* **Autorización:** Gestiona y procesa las decisiones de autorización explícitas del usuario humano.
* **Orquestación de IA:** Coordina la integración del modelo de lenguaje (LLM) y la agregación del contexto recopilado a través de los diferentes clientes.

### 2. Clientes (AI Applications / Agents)

Los clientes MCP son instanciados por la aplicación host para comunicarse con un servidor MCP en particular. Representan las aplicaciones de Inteligencia Artificial o agentes (ej. aplicaciones nativas de Anthropic, Cursor, Windsurf, Goose) que requieren consumir datos o herramientas de sistemas externos. La distinción entre host y cliente es importante: el *host* es la aplicación con la que interactúan las personas, mientras que los *clientes* son los componentes a nivel de protocolo que habilitan las conexiones con los servidores.

Cada cliente es instanciado por el host y sostiene una conexión aislada:

* **Sesiones Aisladas:** Mantiene una sesión con estado único bajo una relación estricta de 1:1 con un servidor específico.
* **Negociación del Protocolo:** Se encarga del intercambio inicial de capacidades y la negociación del protocolo.
* **Ruteo Bidireccional:** Canaliza los mensajes del protocolo de forma bidireccional entre el host y el servidor.
* **Invocación y Control:** Es responsable de invocar herramientas, consultar recursos e interpolar las plantillas de instrucciones. El modelo de lenguaje del cliente decide autónomamente cuándo utilizar una herramienta, mientras que la aplicación cliente retiene el control sobre cómo procesar los recursos.

### 3. Servidores (Wrappers de Contexto)

Los servidores MCP son programas que exponen capacidades específicas a las aplicaciones de IA mediante interfaces de protocolo estandarizadas, funcionando como intermediarios que envuelven sistemas externos (bases de datos, CRMs como Salesforce, sistemas de archivos, repositorios Git, Slack o calendarios) para hacerlos legibles por cualquier cliente compatible.

* **Exposición de Primitivas:** Proveen contexto especializado exponiendo herramientas, recursos y plantillas de instrucciones (*prompts*).
* **Operación Independiente:** Funcionan de manera autónoma con responsabilidades enfocadas y delimitadas, respetando siempre las restricciones de seguridad impuestas.
* **Consumo Universal:** Al implementar una interfaz común, cualquier cliente compatible puede adoptar el servidor con un trabajo de integración mínimo o nulo, resolviendo el problema de acoplamiento de integraciones individuales ($N \times M$).

---

### Características de los Servidores MCP (Primitives)

Los servidores proporcionan tres bloques de construcción esenciales para enriquecer el contexto del modelo de lenguaje. La siguiente tabla resume quién controla cada uno:

| Característica | Descripción | Ejemplos | ¿Quién la controla? |
|---|---|---|---|
| **Tools** | Funciones que el LLM puede invocar activamente, decidiendo cuándo usarlas según la solicitud del usuario. Pueden escribir en bases de datos, llamar APIs externas o modificar archivos. | Buscar vuelos, enviar mensajes, crear eventos de calendario | Modelo |
| **Resources** | Fuentes de datos pasivas de solo lectura que aportan contexto, como contenido de archivos, esquemas de bases de datos o documentación de APIs. | Recuperar documentos, acceder a bases de conocimiento, leer calendarios | Aplicación |
| **Prompts** | Plantillas de instrucciones preconstruidas que indican al modelo cómo trabajar con herramientas y recursos específicos. | Planear unas vacaciones, resumir reuniones, redactar un correo | Usuario |

#### A. Prompts (Instrucciones Estructuradas)

Son plantillas reutilizables y predefinidas que guían las interacciones del modelo, y sirven además para mostrar la mejor forma de usar un servidor MCP concreto. Están diseñadas para ser controladas explícitamente por el usuario a través de invocación explícita —por ejemplo, comandos de la interfaz como *slash commands* ("/planear-vacaciones"), paletas de comandos, botones dedicados o menús contextuales—. Los clientes pueden descubrir los prompts disponibles, recuperar su contenido detallado y pasar argumentos para personalizarlos; también soportan autocompletado de parámetros para ayudar a descubrir valores válidos.

> Los servidores que soportan esta funcionalidad deben declarar explícitamente la capacidad en su inicialización.

**Operaciones del protocolo:**

| Método | Propósito | Retorna |
|---|---|---|
| `prompts/list` | Descubrir los prompts disponibles | Arreglo de descriptores de prompts |
| `prompts/get` | Recuperar el detalle de un prompt | Definición completa del prompt con sus argumentos |

#### B. Resources (Datos de Contexto)

Son fuentes de datos estructuradas (archivos, esquemas de bases de datos, respuestas crudas de APIs) identificadas unívocamente por una URI (por ejemplo, `file:///path/to/document.md`) y que declaran su tipo MIME. Su inclusión está guiada por la aplicación, la cual puede mostrarlos en elementos gráficos (vistas de árbol o lista), permitir búsquedas y filtros, automatizar su inclusión basada en heurísticas de IA, o habilitar selección manual o masiva.

Los recursos admiten dos patrones de descubrimiento:

* **Recursos directos:** URIs fijas que apuntan a datos específicos, por ejemplo `calendar://events/2024`.
* **Plantillas de recursos (Resource Templates):** URIs dinámicas y parametrizables para consultas flexibles, por ejemplo `travel://activities/{city}/{category}`. Estas plantillas incluyen metadatos como título, descripción y tipo MIME esperado, y soportan autocompletado de parámetros (p. ej., escribir "Par" puede sugerir "Paris" o "Park City").

**Operaciones del protocolo:**

| Método | Propósito | Retorna |
|---|---|---|
| `resources/list` | Listar los recursos directos disponibles | Arreglo de descriptores de recursos |
| `resources/templates/list` | Descubrir plantillas de recursos | Arreglo de definiciones de plantillas |
| `resources/read` | Recuperar el contenido de un recurso | Datos del recurso con sus metadatos |
| `subscriptions/listen` | Monitorear cambios en recursos | Flujo (*stream*) de notificaciones de actualización |

Para observar cambios en recursos específicos, el cliente envía una solicitud `subscriptions/listen` indicando las URIs de interés en el filtro `resourceSubscriptions`. El servidor entrega notificaciones `notifications/resources/updated` a través de ese flujo cada vez que un recurso observado cambia.

#### C. Tools (Funciones Ejecutables)

Son funciones del lado del servidor controladas por el modelo de lenguaje, con entradas y salidas tipadas, que el agente puede invocar de forma automática según su comprensión del contexto de la solicitud del usuario. MCP utiliza JSON Schema para la validación. Cuentan con un nombre único y metadatos que describen rigurosamente su esquema de parámetros, permitiendo interactuar activamente con el entorno (APIs, cómputos, escritura de archivos).

Las herramientas pueden requerir el consentimiento del usuario antes de ejecutarse, lo cual ayuda a que las personas mantengan control sobre las acciones que realiza el modelo. Entre los mecanismos de control comunes se incluyen:

* Mostrar las herramientas disponibles en la interfaz, permitiendo habilitarlas o deshabilitarlas para interacciones específicas.
* Diálogos de aprobación para ejecuciones individuales.
* Configuraciones de permisos para pre-aprobar operaciones consideradas seguras.
* Registros de actividad que muestran todas las ejecuciones de herramientas y sus resultados.

**Operaciones del protocolo:**

| Método | Propósito | Retorna |
|---|---|---|
| `tools/list` | Descubrir las herramientas disponibles | Arreglo de definiciones de herramientas con sus esquemas |
| `tools/call` | Ejecutar una herramienta específica | Resultado de la ejecución |

---

### Características de los Clientes MCP

Los clientes pueden implementar funciones complementarias que expanden las capacidades operativas de los servidores conectados. Con la evolución del protocolo, esta familia de características ahora incluye **Elicitation** como mecanismo vigente, mientras que **Roots** y **Sampling** han pasado a un estado de descontinuación.

#### 1. Elicitation (Solicitud de Información al Usuario)

La *elicitation* permite que los servidores soliciten información específica a las personas usuarias durante una interacción, en lugar de exigir todos los datos por adelantado o fallar cuando falta algo. Esto crea flujos de trabajo más dinámicos, en los que el servidor puede pausar su operación para pedir datos puntuales.

Existen dos modalidades:

* **Modo formulario (*form mode*):** el servidor pide al cliente recolectar datos estructurados del usuario; la solicitud incluye un esquema que el cliente utiliza para construir un formulario y validar la respuesta.
* **Modo URL (*URL mode*):** el servidor entrega una URL que el usuario debe abrir; la interacción ocurre fuera de banda y sus datos nunca pasan por el cliente, lo que la hace apropiada para flujos sensibles como el ingreso de credenciales o autorizaciones OAuth de terceros.

El mecanismo sigue el patrón de **Solicitudes de Múltiples Rondas (MRTR)**: cuando un servidor necesita información adicional mientras procesa una solicitud (por ejemplo, `tools/call`), responde con un `InputRequiredResult` cuyo campo `inputRequests` contiene una o más solicitudes `elicitation/create`. El cliente recolecta la información y reintenta la solicitud original, adjuntando las respuestas (`inputResponses`) y el estado (`requestState`) que el servidor haya incluido.

Por razones de privacidad, los servidores no deben usar el modo formulario para solicitar información sensible como contraseñas, llaves de API, tokens de acceso o datos de pago; esas interacciones deben resolverse mediante el modo URL, que mantiene los datos fuera del alcance del cliente y del contexto del LLM.

#### 2. Roots (Límites del Sistema de Archivos)

> **⚠️ Nota de actualización:** *Roots* está **deprecado** a partir de la versión de protocolo `2026-07-28` y programado para su eliminación. Las nuevas implementaciones deben pasar directorios o archivos mediante parámetros de herramientas, URIs de recursos o configuración del servidor, en lugar de este mecanismo.

Permite (o permitía) al cliente exponer de forma estandarizada los límites de los directorios a los que el servidor tiene permitido acceder (`roots`), mejorando la coordinación en operaciones de archivos locales. Los servidores pueden consultar esta lista y recibir alertas cuando cambie. Cada ruta se compone de un campo `uri` (que debe utilizar obligatoriamente el esquema `file://`) y un `name` legible por humanos.

Es importante destacar que los *roots* funcionan como un mecanismo de **coordinación**, no como una frontera de **seguridad**: la especificación indica que los servidores "deberían" (*SHOULD*) respetar estos límites, no que estén obligados a hacerlo, ya que el cliente no puede controlar el código que ejecuta el servidor. La seguridad real debe reforzarse a nivel de sistema operativo, mediante permisos de archivos o sandboxing.

#### 3. Sampling (Muestreo del Modelo)

> **⚠️ Nota de actualización:** *Sampling* también está **deprecado** a partir de la versión de protocolo `2026-07-28`. Las nuevas implementaciones deben integrarse directamente con las APIs de los proveedores de LLM en lugar de depender de este mecanismo.

Proveía un mecanismo estándar para que los servidores solicitaran generaciones de texto o imágenes del LLM a través del cliente, permitiendo comportamientos agénticos anidados dentro de otras características del servidor, sin que el servidor tuviera que integrarse o pagar directamente por el acceso a un modelo. Esto permitía al cliente centralizar el control de accesos, permisos y llaves de API, evitando distribuir credenciales sensibles en cada servidor.

Al igual que la *elicitation*, seguía el patrón MRTR: el `InputRequiredResult` transportaba una solicitud `sampling/createMessage`. Los servidores también podían solicitar el uso de herramientas durante el muestreo (mediante un arreglo `tools` y un campo opcional `toolChoice`), y los clientes debían declarar explícitamente esta capacidad (`sampling.tools`) antes de recibir ese tipo de solicitudes. El diseño priorizaba puntos de control humano: el usuario podía revisar y aprobar tanto la solicitud inicial como la respuesta generada antes de que el servidor continuara.

---

## Ejemplo: Planificación de un viaje con múltiples servidores

El verdadero valor de MCP surge cuando distintos servidores trabajan en conjunto, combinando sus capacidades especializadas a través de una interfaz unificada. Considérese un planificador de viajes con tres servidores conectados: uno de **viajes** (vuelos, hoteles, itinerarios), uno de **clima** (pronósticos) y uno de **calendario/correo** (agenda y comunicaciones).

El flujo típico sería:

1. El usuario invoca el prompt `plan-vacation` con parámetros como destino, fechas, presupuesto y número de viajeros.
2. El usuario selecciona recursos relevantes (por ejemplo, su calendario de junio, sus preferencias de viaje y un viaje anterior a España) para que la aplicación los incorpore como contexto.
3. La IA lee esos recursos, identifica fechas disponibles y preferencias, y luego ejecuta una serie de herramientas: busca vuelos, consulta el clima en el destino, reserva el hotel, crea el evento de calendario y envía el correo de confirmación, solicitando aprobación del usuario cuando corresponde.

Este ejemplo ilustra cómo **Resources** aportan contexto pasivo, **Tools** ejecutan acciones activas, y **Prompts** estructuran el flujo completo —todo orquestado por el host y sus clientes conectados a distintos servidores.

---

## Composabilidad y Multi-Agentes

El principio de **Composabilidad** en MCP establece que la frontera entre un cliente y un servidor es estrictamente lógica y no física. Una misma aplicación, componente o microservicio puede asumir el rol de cliente MCP y servidor MCP simultáneamente, lo que permite encadenar capacidades y construir arquitecturas multiagente sofisticadas a partir de piezas más simples.

---

## Referencias

> Koul, N. (2025, Marzo 27). *The Model Context Protocol (MCP) — A Complete Tutorial*. Medium. https://medium.com/@nimritakoul01/the-model-context-protocol-mcp-a-complete-tutorial-a3abe8a7f4ef

>   Model Context Protocol. (s.f.). *Understanding MCP clients* (especificación versión `2026-07-28`). https://modelcontextprotocol.io/docs/2026-07-28/learn/client-concepts

>   Model Context Protocol. (s.f.). *Understanding MCP servers* (especificación versión `2026-07-28`). https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts
‌
