# 2.1. SDKs y Frameworks Oficiales

## ¿Qué es un SDK?
Un Kit de Desarrollo de Software (SDK, por sus siglas en inglés) es un conjunto de herramientas de creación específicas de plataformas para desarrolladores, proporcionado usualmente por el fabricante de una plataforma de hardware, un sistema operativo o un lenguaje de programación.

Por lo general, un SDK básico incluye un compilador, un depurador y varias interfaces de programación de aplicaciones (API). Asimismo, puede incluir elementos como:
* Documentación
* Bibliotecas
* Editores
* Entornos de tiempo de ejecución
* Controladores
* Protocolos de red

### Beneficios que ofrece un SDK
* **Desarrollo eficiente:** Al proporcionar componentes y bibliotecas prediseñados, ahorran a los desarrolladores un tiempo considerable que antes dedicaban a codificar y depurar desde cero.
* **Implementación más rápida:** Suelen ser compatibles con múltiples plataformas, lo que permite crear e integrar aplicaciones rápidamente.
* **Ahorro de costos:** Reducen el tiempo y los recursos necesarios para desarrollar aplicaciones al permitir construir funcionalidades con rapidez.

---

## Comparativa de SDKs Oficiales para MCP

| Característica | TypeScript | Python | Java |
| :--- | :--- | :--- | :--- |
| **Estado de versión** | V 1.29.0 (Marzo) | V 1.28.1 (Junio) | V 2.0.0 (Junio) |
| **Transportes soportados** | stdio, streamable HTTP | stdio, streamable HTTP, SSE, in-memory | stdio, streamable HTTP |
| **Entornos** | Node.js, Bun, Deno | Python 3.10+ | Java 11+ (JDK / Jakarta EE) |
| **Integración con frameworks** | Express, Hono, Node.js HTTP | Integración directa con CLI / Inspector local | Integración nativa con Spring AI 2.0+ (Spring Boot) |
| **Seguridad** | Helpers de Autenticación, OAuth y validación de cabeceras HTTP | Delegada a la capa de transporte/red y controles del entorno local | Hooks de Autorización conectables |
| **Licencia** | Apache 2.0 / MIT | MIT | MIT |

---

## Fortalezas y Desventajas de los SDKs Oficiales

### TypeScript SDK
* **Fortalezas:**
  * Arquitectura modular que separa el cliente y el servidor en paquetes independientes.
  * Compatibilidad con Standard Schema, permitiendo validar datos con librerías como Zod, Valibot o ArkType.
  * Soporte nativo para entornos de ejecución como Node.js, Bun y Deno.
  * Middleware para integración con frameworks web como Express, Hono y Node.js HTTP.
  * Asistentes integrados para el manejo de autenticación y flujos OAuth.
* **Desventajas:**
  * Mayor complejidad en el registro explícito de herramientas y definición de esquemas.
  * Gestión de versiones que requiere coordinar la transición entre la generación v1 y v2.

### Python SDK
* **Fortalezas:**
  * Reducción de código base mediante abstracciones de FastMCP y el uso de decoradores.
  * Inferencia automática de esquemas JSON a partir de *type hints* y *docstrings* en las funciones.
  * Herramientas de depuración integradas que permiten ejecutar MCP Inspector desde la interfaz de línea de comandos.
  * Capacidad de ejecutar clientes y servidores directamente en memoria para pruebas unitarias.
* **Desventajas:**
  * Dependencia de versiones recientes de Python (3.10+) y uso riguroso de tipado para la generación de esquemas.
  * Delegación de los esquemas de autorización a la capa de transporte o servidor web subyacente.

### Java SDK
* **Fortalezas:**
  * Arquitectura modular desacoplada orientada a entornos empresariales.
  * Modelo de programación basado en Reactive Streams para alta concurrencia, con fachadas síncronas para casos de uso tradicionales.
  * Integración con Spring Boot y Spring AI para la implementación de seguridad.
  * Validación mediante conjuntos de pruebas de conformidad oficial del protocolo.
* **Desventajas:**
  * Curva de aprendizaje elevada debido al modelo de programación reactiva con Project Reactor.
  * Mayor complejidad en la configuración de dependencias de construcción en Maven o Gradle.

---

## Referencias
> Amazon Web Services. (2023, Marzo 13). *¿Qué es un SDK?* Amazon Web Services, Inc. https://aws.amazon.com/es/what-is/sdk/

> Model Context Protocol. (s.f.). *SDKs*. Model Context Protocol. https://modelcontextprotocol.io/docs/sdk

> Model Context Protocol. (2026, Junio 11). *modelcontextprotocol/java-sdk: The official Java SDK for Model Context Protocol servers and clients*. GitHub. https://github.com/modelcontextprotocol/java-sdk

> Model Context Protocol. (2026, Junio 26). *modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients*. GitHub. https://github.com/modelcontextprotocol/python-sdk

> Model Context Protocol. (2026, Marzo 30). *modelcontextprotocol/typescript-sdk: The official TypeScript SDK for Model Context Protocol servers and clients*. GitHub. https://github.com/modelcontextprotocol/typescript-sdk

> Red Hat. (2023, Agosto 4). *SDK: ¿qué es y para qué sirve?* Redhat.com. https://www.redhat.com/es/topics/cloud-native-apps/what-is-SDK
