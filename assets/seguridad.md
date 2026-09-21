# 3.1 Seguridad en MCP

## ¿Qué es la Seguridad MCP?

Los servidores MCP centralizan credenciales de múltiples servicios empresariales en un solo lugar, lo que los convierte en un punto único de falla: si ese servidor se ve comprometido, expone a toda la organización. Un servidor MCP vulnerado e implementado sin controles de autenticación puede otorgarle a un atacante acceso a todas las bases de datos, sistemas de archivos y servicios en la nube a los que el asistente de IA está conectado. Este patrón de vulnerabilidad se materializó en el mundo real en el caso **CVE-2025-49596** (CVSS 9.4), donde atacantes lograron ejecutar comandos arbitrarios a través de instancias de MCP Inspector sin autenticación.

Al desplegar un servidor MCP se crea un puente entre los motores de razonamiento de la IA y la infraestructura empresarial: ese servidor almacena tokens OAuth de múltiples servicios, ejecuta comandos del sistema, lee archivos y consulta bases de datos. Los equipos de seguridad enfrentan hoy múltiples categorías de vulnerabilidades ya documentadas, incluyendo tres CVE críticas registradas en la National Vulnerability Database. El primer paquete MCP malicioso conocido apareció en septiembre de 2025 y operó sin ser detectado durante dos semanas mientras exfiltraba datos de correo electrónico.

## Relación entre la Seguridad MCP y la Ciberseguridad

La seguridad MCP se relaciona con disciplinas como la gestión de identidades y accesos, la seguridad de la cadena de suministro, y ataques específicos de IA que las herramientas de seguridad tradicionales no fueron diseñadas para detectar. La arquitectura del protocolo define tres límites de seguridad:

* La **capa de transporte**, que gestiona la comunicación entre clientes y servidores.
* La **capa de protocolo**, encargada de la mensajería JSON-RPC 2.0 para la negociación del ciclo de vida y de capacidades.
* La **capa de datos**, que define las herramientas, recursos, prompts y notificaciones a las que acceden los agentes.

El 22 de mayo de 2025, CISA emitió una guía conjunta que subraya que la seguridad de los datos es esencial para garantizar la confiabilidad de los sistemas de IA, un reconocimiento gubernamental de que la infraestructura de agentes de IA forma parte del panorama de amenazas que los equipos de un SOC deben vigilar. En paralelo, el proyecto OWASP MCP Top 10 estableció el primer marco estándar de la industria para clasificar los riesgos de MCP, aportando una metodología estructurada de evaluación para los equipos que evalúan la integración de IA en sus organizaciones.

## Componentes Principales de la Seguridad MCP

La arquitectura de seguridad MCP debe cubrir controles en cinco frentes: arquitectura, gestión de accesos, identificación de amenazas y gobernanza.

* **Capa de autenticación y autorización:** los servidores MCP requieren OAuth 2.1 con PKCE, delimitación de capacidades (*scopes*) y prevención del acceso a tokens de alcance amplio mediante fugas en logs o *scraping* de memoria.
* **Seguridad de transporte:** habilitar TLS 1.2 o superior con suites de cifrado robustas, implementar TLS mutuo (mTLS) para las comunicaciones entre servidores, y activar protección contra *DNS rebinding*. NOTA IMPORTANTE: según el aviso de seguridad GHSA-w48q-cv73-mx4w de GitHub, el SDK de TypeScript para MCP no habilita esta última protección por defecto.
* **Canal de validación de herramientas:** los controles de seguridad deben validar en tres etapas: (1) filtrado basado en patrones para detectar comandos e inyección de prompts, (2) identificación neuronal para detectar ataques semánticos en las descripciones de las herramientas, y (3) arbitraje basado en un LLM para resolver casos límite.
* **Gestión de credenciales:** se recomienda usar bóvedas empresariales como AWS Secrets Manager o HashiCorp Vault, implementar rotación automática, utilizar tokens de corta duración, y proteger contra fugas en logs y *scraping* de memoria.
* **Infraestructura de identificación y monitoreo:** registrar todas las operaciones MCP (invocaciones de herramientas con sus parámetros, intentos de autenticación, accesos a recursos y violaciones de alcance) y correlacionar los eventos MCP con el comportamiento de identidad y el tráfico de red.

## Cómo Funciona la Seguridad MCP

La seguridad MCP opera mediante controles en capas que protegen cada etapa de la interacción entre los agentes de IA y los sistemas empresariales:

1. **Arquitectura de gateway centralizado:** un proxy centralizado aplica políticas de forma consistente, monitorea el comportamiento y hace cumplir restricciones. Este gateway impone listas de servidores MCP aprobados, centraliza el control de acceso y la identificación, e inspecciona todas las invocaciones de herramientas, evitando que servidores no autorizados accedan a recursos empresariales sin importar cómo los desarrolladores configuren sus entornos locales.
2. **Fase de negociación de capacidades:** durante la inicialización, el gateway compara las capacidades solicitadas por el servidor contra las reglas de política vigentes, bloqueando aquellos que soliciten permisos excesivos. Los controles de acceso granulares asignan roles de usuario específicos a capacidades de herramientas concretas.
3. **Fase de ejecución en tiempo real:** cuando un agente de IA invoca una herramienta MCP, la capa de seguridad valida los parámetros de entrada en busca de ataques de inyección, aísla la ejecución de la herramienta y registra el contexto forense completo.
4. **Identificación continua:** las plataformas de seguridad analizan el tráfico MCP mediante un canal de identificación de varias etapas que combina filtrado basado en patrones, análisis de redes neuronales e identificación de anomalías de comportamiento.
5. **Flujo de respuesta a incidentes:** cuando se detecta actividad MCP maliciosa, las capacidades de respuesta autónoma aíslan los servidores comprometidos, revocan las credenciales asociadas en todos los servicios integrados, revierten cambios no autorizados y reconstruyen la línea de tiempo completa del ataque para su investigación posterior.

## Por Qué Importa la Seguridad MCP

* **Riesgo de agregación de credenciales:** al almacenar tokens OAuth de múltiples servicios en un solo lugar, los servidores MCP crean un único punto de falla; si se ven comprometidos, el atacante obtiene acceso amplio a todos los servicios conectados, lo que exige procedimientos de respuesta a incidentes específicos para MCP.
* **Validación de la cadena de suministro:** las rutas de integración sencillas de MCP introducen riesgos a través de servidores no confiables, tal como evidenció el primer paquete MCP malicioso detectado en septiembre de 2025, que exfiltró datos de correo electrónico durante dos semanas sin ser detectado.
* **Marcos de gobernanza:** es necesario establecer control sobre las capas de integración MCP que no están siendo monitoreadas, aplicando políticas centralizadas a nivel de gateway, flujos de aprobación para nuevos servidores y bases de seguridad alineadas con la clasificación de los datos.
* **Arquitectura de confianza cero:** constituye la base de la seguridad MCP, exigiendo TLS mutuo entre microservicios MCP, control de tráfico basado en identidad y seguridad independiente de la topología de red.
* **Cumplimiento y alineación regulatoria:** protege a las organizaciones cuando los agentes de IA acceden a datos regulados. La guía de CISA de mayo de 2025 establece que la seguridad de los datos garantiza la confiabilidad de los sistemas de IA, por lo que los controles de seguridad MCP deben demostrar que el acceso de los asistentes de IA a los datos sigue la misma gobernanza aplicada a los usuarios humanos.


## Desafíos en la Implementación de la Seguridad MCP

* **Brechas arquitectónicas:** la responsabilidad de la seguridad recae completamente en los equipos de implementación, sin orientación a nivel de protocolo, ya que la propia especificación de MCP indica explícitamente que no puede aplicar estos principios de seguridad a nivel de protocolo, lo que genera un desajuste entre las expectativas de los desarrolladores y la realidad de la seguridad.
* **Limitaciones de visibilidad:** las herramientas de monitoreo tradicionales tienen dificultades para interpretar los patrones de mensajería JSON-RPC 2.0 y las implementaciones distribuidas, lo que exige instrumentación personalizada para rastrear la actividad de los servidores MCP.
* **Proliferación de herramientas:** las organizaciones suelen implementar servidores MCP en distintos departamentos sin gobernanza centralizada; sin un inventario centralizado, los equipos de seguridad no pueden aplicar controles consistentes ni rastrear qué servidores tienen acceso a credenciales sensibles.
* **Nuevos patrones de ataque:** ataques semánticos como el envenenamiento de herramientas y el *shadowing* eluden por completo las herramientas de detección basadas en firmas, y requieren modelos conscientes del contexto capaces de comprender la manipulación del lenguaje natural.
* **Complejidad en la respuesta a incidentes:** un solo compromiso puede afectar a múltiples servicios simultáneamente. Los *playbooks* de respuesta existentes suelen asumir la contención de un solo servicio, mientras que los incidentes MCP requieren revocación coordinada de credenciales en todos los sistemas integrados, así como análisis forense que abarque identidad, seguridad de endpoints y seguridad en la nube.

## Errores Comunes en la Seguridad MCP

* **Implementación sin autenticación:** es común desplegar servidores MCP accesibles en la red sin mecanismos de autenticación. Ejecutar un servidor MCP sin autenticación no se considera una práctica recomendable, ya que los atacantes pueden descubrir estos servidores expuestos mediante escaneo de puertos, conectarse sin credenciales y ejecutar herramientas arbitrarias con privilegios completos.
* **Pobre implementación de sandbox:** los análisis de brechas de seguridad han identificado la falta de contención de directorios como causa raíz en incidentes documentados. Los servidores MCP que ejecutan operaciones de archivos sin validar rutas permiten ataques de recorrido de directorios, dando a los atacantes acceso a archivos de configuración que contienen contraseñas de bases de datos, claves de API y credenciales en la nube.
* **Instalación de servidores no confiables:** algunos equipos instalan servidores MCP provenientes de fuentes no confiables, sin revisión de código ni escaneo de seguridad. Se han documentado servidores MCP maliciosos que se presentan como herramientas legítimas mientras implementan robo de credenciales, además de casos donde herramientas previamente aprobadas cambian su comportamiento tras el despliegue (ataques *rug pull*) sin que nadie los detecte a tiempo.
* **Alcances de autorización excesivos:** los atacantes pueden obtener tokens de acceso con alcances muy amplios (por ejemplo, `files:*`, `db:*` o `admin:*`) mediante fugas en logs, *scraping* de memoria o intercepción local. Los servidores MCP que solicitan todos los permisos disponibles durante la autorización inicial no están aplicando una delimitación de permisos adecuada a nivel de capacidad.
* **Monitoreo insuficiente:** una telemetría limitada en los sistemas MCP dificulta cualquier investigación posterior. Los registros de seguridad que omiten detalles críticos no permiten reconstruir la línea de tiempo de un ataque; el monitoreo debe incluir el registro de todas las operaciones, el seguimiento de los intentos de autenticación y garantizar la integración con un SIEM.

## Mejores Prácticas de Seguridad MCP

* **Implementar una arquitectura de gateway MCP centralizado** como control arquitectónico fundamental: el gateway actúa como proxy de toda la comunicación MCP, aplica listas de servidores aprobados, centraliza el control de acceso y la identificación, e inspecciona todas las invocaciones de herramientas. Este patrón ofrece un único punto de control para aplicar políticas de forma consistente en todos los flujos de trabajo de los agentes.
* **Aplicar el principio de mínimo privilegio** con gestión granular de alcances a nivel de capacidad:
  * Asignar roles de usuario a capacidades de herramientas específicas.
  * Validar las solicitudes de alcance de forma dinámica durante la autorización.
  * Usar delimitación de permisos a nivel de capacidad en lugar de tokens de alcance amplio.
  * Proteger contra el robo de tokens mediante fugas en logs, *scraping* de memoria o intercepción local.
* **Establecer controles de seguridad de la cadena de suministro** antes de cualquier implementación en producción: pruebas de seguridad estática de aplicaciones y escaneo de vulnerabilidades en todos los servidores, verificación criptográfica de la integridad del servidor, y escaneo de paquetes en busca de malware o instrucciones maliciosas ocultas. Se recomienda fijar versiones específicas de los servidores MCP y alertar a los administradores ante cualquier cambio.
* **Implementar canales de identificación en múltiples capas** diseñados específicamente para el envenenamiento de herramientas y los ataques semánticos, siguiendo el enfoque de tres etapas: filtrado basado en patrones para inyección de comandos, identificación neuronal para ataques semánticos en descripciones de herramientas, y arbitraje basado en un LLM para casos límite donde los adversarios manipulan los metadatos de las herramientas para engañar a los agentes de IA.
* **Implementar registros de auditoría integrados con plataformas SIEM:** la infraestructura de logging debe capturar cada invocación de herramienta con su contexto completo, y monitorear patrones anómalos, incluyendo secuencias inusuales de acceso a herramientas, intentos de escalamiento de privilegios e indicadores de exfiltración de datos.
* **Proteger la gestión de credenciales y secretos** mediante bóvedas empresariales: integrar soluciones como AWS Secrets Manager o HashiCorp Vault para proteger claves de API y credenciales OAuth, implementar rotación automática y tokens de corta duración, y proteger contra fugas en logs y *scraping* de memoria mediante una bóveda de tokens segura.
* **Habilitar la seguridad de transporte y los controles de red:** exigir TLS 1.2 o superior con suites de cifrado robustas, implementar TLS mutuo para las comunicaciones entre servidores, y aislar los servidores MCP en segmentos de red dedicados con reglas de firewall apropiadas.
* **Establecer marcos de gobernanza con aplicación autónoma de políticas:** las políticas formales de uso de MCP deben alinearse con la clasificación de los datos y los estándares de control de acceso; la aplicación autónoma de políticas a nivel de gateway, los flujos de aprobación para nuevas implementaciones de servidores, las revisiones periódicas de seguridad sobre los patrones de acceso a herramientas y los controles de prevención de pérdida de datos ayudan a evitar la exposición de información sensible a través de las integraciones MCP.

---

## Referencias

> SentinelOne. (2026, Marzo 30). *Seguridad de Model Context Protocol (MCP): Guía completa*. SentinelOne. https://www.sentinelone.com/es/cybersecurity-101/cybersecurity/mcp-security/
