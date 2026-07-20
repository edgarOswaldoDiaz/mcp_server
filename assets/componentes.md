# 1.3 Componentes y Características del Ecosistema MCP

## Arquitectura de Componentes del Ecosistema

El ecosistema de *Model Context Protocol* opera mediante la interacción lógica de componentes definidos que dividen las responsabilidades de control, mediación y aprovisionamiento de capacidades.

### 1. Host (Proceso Coordinador)
El proceso *Host* actúa como el contenedor principal y el orquestador del entorno de ejecución. Sus responsabilidades clave incluyen:
*   **Gestión de Instancias:** Crea y administra de forma centralizada múltiples instancias de clientes.
*   **Ciclo de Vida y Conexiones:** Controla los permisos de conexión y el ciclo de vida de cada cliente acoplado.
*   **Políticas de Seguridad:** Ejecuta y hace cumplir las políticas de seguridad institucional junto con los requerimientos de consentimiento del usuario.
*   **Autorización:** Gestiona y procesa las decisiones de autorización explícitas del usuario humano.
*   **Orquestación de IA:** Coordina la integración del modelo de lenguaje (LLM) y la agregación del contexto recopilado a través de los diferentes clientes.

### 2. Clientes (AI Applications / Agents)
Los clientes MCP representan las aplicaciones de Inteligencia Artificial o agentes (ej. aplicaciones nativas de Anthropic, Cursor, Windsurf, Goose) que requieren consumir datos o herramientas de sistemas externos. Cada cliente es instanciado por el host y sostiene una conexión aislada:
*   **Sesiones Aisladas:** Mantiene una sesión con estado único bajo una relación estricta de 1:1 con un servidor específico.
*   **Negociación del Protocolo:** Se encarga del intercambio inicial de capacidades y la negociación del protocolo.
*   **Ruteo Bidireccional:** Canaliza los mensajes del protocolo de forma bidireccional entre el host y el servidor.
*   **Invocación y Control:** Es responsable de invocar herramientas, consultar recursos e interpolar las plantillas de instrucciones. En este componente, el modelo de lenguaje del cliente decide autónomamente cuándo utilizar una herramienta, mientras que la aplicación cliente retiene el control sobre cómo procesar los recursos.

### 3. Servidores (Wrappers de Contexto)
Los servidores MCP funcionan como intermediarios estandarizados que envuelven sistemas externos (bases de datos, CRMs como Salesforce, sistemas de archivos o repositorios Git) para hacerlos legibles por cualquier cliente compatible.
*   **Exposición de Primitivas:** Proveen contexto especializado exponiendo herramientas, recursos y plantillas de instrucciones (*prompts*).
*   **Operación Independiente:** Funcionan de manera autónoma con responsabilidades enfocadas y delimitadas, respetando siempre las restricciones de seguridad impuestas.
*   **Consumo Universal:** Al implementar una interfaz común, cualquier cliente compatible puede adoptar el servidor con un trabajo de integración mínimo o nulo, resolviendo el problema de acoplamiento de integraciones individuales ($N \times M$).

---

## Características de los Servidores MCP (Primitives)

Los servidores proporcionan bloques de construcción esenciales para enriquecer el contexto del modelo de lenguaje:

### A. Prompts (Instrucciones Estructuradas)
Son plantillas predefinidas que guían las interacciones del modelo. Están diseñadas para ser controladas explícitamente por el usuario a través de comandos de la interfaz (como *slash commands*). Los clientes pueden descubrir los prompts disponibles, recuperar su contenido y pasar argumentos para personalizarlos. 

> Los servidores que soportan esta funcionalidad deben declarar explícitamente la capacidad en su inicialización.



### B. Resources (Datos de Contexto)
Son fuentes de datos estructuradas (archivos, esquemas de bases de datos, respuestas crudas de APIs) identificadas unívocamente por una URI. Su inclusión está guiada por la aplicación, la cual puede mostrarlos en elementos gráficos (vistas de árbol), permitir búsquedas o automatizar su inclusión basada en heurísticas.

Los servidores que implementan recursos declaran la capacidad permitiendo dos funciones opcionales:
*   `subscribe`: Permite al cliente suscribirse a cambios en recursos individuales.
*   `listChanged`: Emite notificaciones reactivas si la lista de recursos varía.



### C. Tools (Funciones Ejecutables)
Son funciones del lado del servidor controladas por el modelo de lenguaje, que el agente puede invocar de forma automática según su comprensión del contexto. Cuentan con un nombre único y metadatos que describen rigurosamente su esquema de parámetros, permitiendo interactuar activamente con el entorno (APIs, cómputos).



---

## Características de los Clientes MCP

Los clientes pueden implementar funciones complementarias que expanden las capacidades operativas de los servidores conectados:

### 1. Roots (Límites del Sistema de Archivos)
Permite al cliente exponer de forma estandarizada los límites de los directorios a los que el servidor tiene permitido acceder (`roots`), mejorando la seguridad en operaciones de archivos locales. Los servidores pueden consultar esta lista y recibir alertas cuando cambie. Cada ruta se compone de un campo `uri` (que debe utilizar obligatoriamente el esquema `file://`) y un `name` legible por humanos.


### 2. Sampling (Muestreo del Modelo)
Provee un mecanismo estándar para que los servidores soliciten generaciones de texto o imágenes del LLM a través del cliente, permitiendo comportamientos agénticos anidados dentro de otras características del servidor. Esto permite al cliente centralizar el control de accesos, permisos y llaves de API, evitando tener que distribuir credenciales sensibles en cada servidor.

---

## Composabilidad y Multi-Agentes

El principio de **Composabilidad** en MCP establece que la frontera entre un cliente y un servidor es estrictamente lógica y no física. Una misma aplicación, componente o microservicio puede asumir el rol de cliente MCP y servidor MCP simultáneamente.

---

## Referencias
> Koul, N. (2025, Marzo 27). *The Model Context Protocol (MCP) — A Complete Tutorial*. Medium. https://medium.com/@nimritakoul01/the-model-context-protocol-mcp-a-complete-tutorial-a3abe8a7f4ef
‌
