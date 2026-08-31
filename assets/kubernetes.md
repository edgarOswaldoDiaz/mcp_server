# Kubernetes

## ¿Qué es Kubernetes?

Kubernetes es un software de código abierto que automatiza la implementación, la administración y el escalado de aplicaciones en contenedores. Organiza clústeres de máquinas, programa contenedores y proporciona recuperación automática, equilibrio de carga y portabilidad entre entornos.

Docker resuelve **empaquetar** una aplicación (por ejemplo, un servidor MCP) en un contenedor portable. Pero cuando una organización necesita ejecutar **varios** contenedores (por ejemplo, varios servidores MCP simultáneamente), escalarlos de forma independiente, y recuperarlos automáticamente ante fallos, coordinar todo eso manualmente se vuelve inviable. Kubernetes aborda esa complejidad con una API declarativa y un sistema de control que decide qué debe ejecutarse y lo mantiene en ejecución.

## Por qué es relevante para una arquitectura MCP

En un despliegue local de organización con múltiples servidores MCP (uno para la base de datos, otro para Slack, otro para el filesystem interno, etc.), Kubernetes permite:

- Ejecutar cada servidor MCP como una unidad independiente y escalable.
- Exponer cada servidor internamente en la red mediante una dirección estable, aunque los contenedores que lo respaldan cambien.
- Recuperar automáticamente un servidor que falla, sin intervención manual.
- Actualizar un servidor MCP a una nueva versión de forma progresiva, con reversión automática si algo sale mal.

## Características principales

-  **Auto-reparación**
Reinicia contenedores que fallan, sustituye y reprograma contenedores cuando los nodos mueren, y elimina de servicio los contenedores que no responden a las pruebas de salud definidas, sin exponerlos a los clientes hasta que estén listos.

- **Orquestación de almacenamiento**
Monta automáticamente el sistema de almacenamiento elegido, ya sea local, de un proveedor de nube pública, o un sistema en red como iSCSI o NFS. Relevante para servidores MCP que necesitan persistencia (ej. cachés, logs, o datos temporales).

- **Despliegues y rollback automáticos**
Despliega cambios de forma progresiva mientras monitoriza la salud de la aplicación, para no eliminar todas las instancias al mismo tiempo. Si algo sale mal, revierte el cambio automáticamente.

- **Bin packing automático**
Coloca los contenedores en los nodos según los recursos solicitados y otras restricciones, sin afectar la disponibilidad, combinando cargas críticas y de mejor esfuerzo para aprovechar mejor los recursos del clúster.

- **Gestión de secretos y configuración**
Permite desplegar y actualizar credenciales (por ejemplo, tokens de acceso que un servidor MCP necesita para conectarse a una API interna) sin reconstruir la imagen del contenedor ni exponerlas en archivos de configuración.

- **Ejecución en lotes**
Además de servicios, gestiona trabajos por lotes o de integración continua, sustituyendo los contenedores que fallen si así se desea.

## Glosario rápido de objetos

| Objeto | Descripción |
|---|---|
| **Pod** | Unidad básica que ejecuta uno o varios contenedores. Kubernetes programa Pods, no contenedores individuales. |
| **Deployment** | Describe el estado deseado de una aplicación (cuántas réplicas, qué imagen) y gestiona actualizaciones y reversiones. |
| **Service** | Dirección estable (IP o nombre de host) para un conjunto de Pods que cambian con el tiempo. |
| **Node** | Máquina del clúster donde se ejecutan los Pods. |
| **Control Plane** | Componentes que administran el estado del clúster y las decisiones de programación (`kube-apiserver`, `etcd`, `kube-scheduler`, `kube-controller-manager`). |

## Cómo encajarían los servidores MCP en este modelo

Un patrón típico de despliegue sería:

1. Cada servidor MCP se empaqueta como imagen Docker.
2. Se declara como un **Deployment** en Kubernetes, especificando cuántas réplicas se necesitan.
3. Se expone mediante un **Service** para que el host/cliente MCP pueda alcanzarlo con una dirección estable dentro de la red interna.
4. Si un servidor recibe más carga de la esperada, se puede escalar horizontalmente aumentando sus réplicas.
5. Si un Pod falla o el nodo donde corre deja de responder, Kubernetes lo reemplaza o reprograma automáticamente, sin intervención manual.

## Docker Compose vs. Kubernetes: cuándo usar cada uno

| Escenario | Herramienta recomendada |
|---|---|
| Prototipo o piloto con pocos usuarios | Docker Compose |
| Un solo servidor MCP, sin necesidad de alta disponibilidad | Docker Compose |
| Múltiples servidores MCP en producción, con distintos equipos consumiéndolos | Kubernetes |
| Necesidad de escalado automático o recuperación ante fallos sin intervención manual | Kubernetes |


## Referencias
> Amazon Web Services. (s.f.). *¿Qué es Kubernetes?* Amazon Web Services, Inc. https://azure.microsoft.com/es-mx/resources/cloud-computing-dictionary/what-is-kubernetes

> The Kubernetes Authors. (2026). *Orquestación de contenedores para producción.* Kubernetes. https://kubernetes.io/es/

> The Kubernetes Authors. (s.f.). *Kubernetes Documentation. Overview*. Kubernetes. https://kubernetes.io/docs/concepts/overview/#why-you-need-kubernetes-and-what-can-it-do
