# 2.1.3 Contenedores

## ¿Qué son los Contenedores?

Los contenedores son unidades ejecutables de software que empaquetan el código de una aplicación, permitiendo que dicho código se ejecute de manera consistente en cualquier entorno informático. Estos paquetes ligeros incluyen no solo el código de la aplicación, sino también los elementos necesarios para su correcto funcionamiento, como versiones específicas de entornos de ejecución de determinados lenguajes de programación y las bibliotecas indispensables para operar los servicios de software correspondientes.

Los contenedores se apoyan en una forma de virtualización a nivel de sistema operativo (SO): en lugar de virtualizar hardware completo, aprovechan características propias del kernel del SO para aislar procesos entre sí, sin necesidad de replicar un sistema operativo completo por cada aplicación.

## Ventajas

* **Ligeros:** al compartir el kernel del sistema operativo de la máquina anfitriona, los contenedores eliminan la necesidad de contar con una instancia completa del SO por cada aplicación. Esto hace que sus archivos sean considerablemente más pequeños y fáciles de manejar en comparación con otras formas de virtualización.
* **Portátiles e independientes:** al llevar consigo todas sus dependencias, el código de una aplicación puede escribirse una única vez y ejecutarse en distintos entornos sin necesidad de reconfigurarlo cada vez.
* **Compatibles con arquitecturas modernas:** la combinación de portabilidad y coherencia entre plataformas convierte a los contenedores en una opción ideal para patrones de diseño contemporáneos como DevOps, *Serverless* y microservicios.

## Casos de Uso

### Microservicios

Debido a su tamaño reducido y ligereza, los contenedores resultan especialmente adecuados para arquitecturas de microservicios, en las que una aplicación se construye a partir de numerosos servicios débilmente acoplados que pueden desplegarse de manera independiente entre sí. Bajo este enfoque, cada microservicio puede empaquetarse en su propio contenedor y desplegarse sin depender directamente de los demás.

### DevOps

La combinación de microservicios como arquitectura y contenedores como plataforma de despliegue constituye una base habitual para los equipos de desarrollo y operaciones que adoptan metodologías DevOps. En particular, los contenedores facilitan la implementación de *pipelines* DevOps, incluyendo procesos de integración continua y despliegue continuo (CI/CD).

### Entornos Híbridos y Multinube

Puesto que los contenedores pueden ejecutarse de forma coherente en prácticamente cualquier entorno, constituyen una arquitectura subyacente idónea para escenarios de nube híbrida y multinube, en los que una organización opera combinando múltiples proveedores de nube pública junto con su propio centro de datos.

### Cargas de Trabajo de IA y ML

La contenerización permite que los pipelines de DevOps desplieguen de forma ágil aplicaciones de inteligencia artificial (IA) y *machine learning* (ML) en entornos de computación en la nube, simplificando la gestión de sus dependencias y requerimientos específicos.

### IA Generativa

Los contenedores también constituyen una forma eficiente de desplegar y gestionar los modelos de lenguaje grande (LLM) asociados a la IA generativa, aportando portabilidad y escalabilidad cuando se combinan con herramientas de orquestación. Adicionalmente, cualquier cambio realizado sobre un LLM puede empaquetarse rápidamente en una nueva imagen de contenedor, lo que agiliza considerablemente los ciclos de desarrollo y pruebas.

## Relación con el MCP
 
Cuando un servidor MCP debe compartirse entre equipos o implementarse en un entorno de producción, se recomienda integrarlo en un contenedor siguiendo las mismas herramientas y procesos de diseño que se utilizan para cualquier otra aplicación empresarial. Este enfoque aporta uniformidad a la hora de gestionar, desplegar y proteger estos componentes: se define la imagen del contenedor, se construye, se publica en un registro y se despliega mediante alguna plataforma de orquestación de contenedores. 
Las mismas herramientas de compilación habituales permiten además firmar y verificar los servidores MCP, generar una lista de materiales de software (SBOM) o almacenarlos en repositorios de artefactos, prácticas que refuerzan la trazabilidad y la seguridad de la cadena de suministro de software.
 
Al igual que con cualquier otro software, un servidor MCP no está exento de recibir código malicioso, por lo que conviene analizarlo y validarlo de forma permanente con herramientas de escaneo de vulnerabilidades, con el fin de detectar dependencias maliciosas o infracciones a las políticas de seguridad de la organización.
 
### Ventajas de contenerizar servidores MCP
 
Un servidor MCP empaquetado en un contenedor puede escalarse horizontalmente para atender incrementos de carga, supervisarse con herramientas estándar de observabilidad, e integrarse con las políticas de seguridad y control de acceso ya existentes en la organización (por ejemplo, mediante control de acceso basado en roles). Además, es común que estos servidores admitan modos de acceso configurables, solo lectura, no destructivo o acceso completo, para ajustar el nivel de exposición según el contexto en el que se implementen.
 
Alrededor de los servidores MCP en contenedores ya existe un ecosistema de herramientas en crecimiento: operadores de ciclo de vida que facilitan su despliegue y conexión con agentes, puertas de enlace (*gateways*) especializadas que añaden funciones avanzadas de seguridad empresarial, y el soporte de plataformas de contenedores (como Docker, Podman, Kubernetes).
 
### Cuándo NO conviene contenerizar un servidor MCP
 
No todos los servidores MCP se benefician de la contenerización. La especificación de MCP admite dos mecanismos de transporte principales, y esta distinción resulta clave a la hora de decidir si conviene o no empaquetar un servidor en un contenedor:
 
* **Transporte stdio (entrada/salida estándar):** el servidor se comunica a través de flujos de proceso, y es el propio cliente de IA quien lo genera como un proceso secundario (*subproceso*). Este modelo funciona bien en escenarios de un solo usuario —como el asistente de codificación de una persona desarrolladora, una herramienta de productividad local o un script de automatización personal—, donde el servidor corre en la misma máquina del usuario, accede a archivos y recursos locales, y termina su ejecución cuando ya no se necesita. Contenerizar este tipo de servidores suele añadir complejidad innecesaria sin aportar beneficios reales para casos de uso locales y de un solo usuario.
* **Transportes basados en HTTP** (incluyendo *Streamable HTTP* y el transporte heredado de eventos enviados por el servidor, SSE): el servidor se ejecuta como un proceso independiente capaz de gestionar múltiples conexiones de clientes de forma simultánea, exponiendo *endpoints* de red y comportándose de manera similar a un servicio web tradicional. Este tipo de servidores sí son candidatos naturales para la contenerización, ya que se benefician directamente de un despliegue, escalado y gestión centralizados.
### Marco de decisión
 
En términos generales, la decisión de contenerizar o no un servidor MCP puede resumirse así:
 
| Escenario | Recomendación |
|---|---|
| Entornos compartidos o de producción (equipo, acceso por red, servidor) | Contenerizar |
| Agente en contenedor + servidor MCP por stdio | Ejecutar el servidor en el **mismo** contenedor que el agente |
| Agente en contenedor + servidor MCP por HTTP | Ejecutar el servidor en un contenedor **separado** |
| Uso local, un solo usuario, transporte stdio | La contenerización es opcional; puede generar sobrecarga innecesaria |
 
En resumen, la contenerización no es un requisito universal para todo servidor MCP, sino una decisión que depende principalmente del mecanismo de transporte utilizado y del alcance de la implementación: mientras más compartido, distribuido o expuesto a la red esté un servidor MCP, mayor es el beneficio de empaquetarlo y gestionarlo como un contenedor.
 
---
 
## Referencias
 
> Google Cloud. (s.f.). *¿Qué son los contenedores?* Google Cloud. https://cloud.google.com/learn/what-are-containers?hl=es

> Red Hat. (2026, Marzo 31). *Uso de contenedores para aplicar el rigor de la ingeniería de software a las cargas de trabajo de inteligencia artificial*. Red Hat.com. https://www.redhat.com/es/blog/using-containers-bring-software-engineering-rigor-ai-workloads
 
> Susnjara, S. & Smalley, I. (2024, Mayo 9). *¿Qué son los contenedores?* IBM.com. https://www.ibm.com/mx-es/think/topics/containers
 
