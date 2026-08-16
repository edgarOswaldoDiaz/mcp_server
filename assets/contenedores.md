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

---

## Referencias

> Google Cloud. (s.f.). *¿Qué son los contenedores?* Google Cloud. https://cloud.google.com/learn/what-are-containers?hl=es

> Susnjara, S. & Smalley, I. (2024, Mayo 9). *¿Qué son los contenedores?* IBM.com. https://www.ibm.com/mx-es/think/topics/containers
