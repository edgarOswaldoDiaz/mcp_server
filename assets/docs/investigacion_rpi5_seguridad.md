# Optimización de SO y Hardening de Contenedores para Raspberry Pi 5 (16GB)
**Fecha de Avance:** 9 de noviembre de 2026
**Rol:** Seguridad de Persistencia y Contenedores

## 1. Sistema Operativo y Kernel Optimizado
Para aprovechar los 16GB de RAM de la Raspberry Pi 5 (arquitectura ARM64) en un entorno de agentes computacionales y ciencia de datos, se descartan SO de escritorio. 
* **SO Recomendado:** Alpine Linux o Ubuntu Server 24.04 LTS (versión mínima).
* **Optimización del Kernel:** Habilitar `cgroups v2` (Control Groups) para una gestión estricta de memoria y CPU, y `namespaces` para el aislamiento de procesos. Deshabilitar módulos del kernel innecesarios (Bluetooth, Wi-Fi si se usa Ethernet, audio) para reducir la superficie de ataque.

## 2. Hardening (Endurecimiento) de Docker 
Para cumplir con las normativas de seguridad, el entorno contenerizado implementa las siguientes directivas de protección:

* **Modo Rootless:** Ejecutar el demonio de Docker sin privilegios de superusuario (root) para evitar escalamiento de privilegios si un contenedor es comprometido.
* **Límites de Recursos (Prevención DoS):** Asignación estricta de memoria (ej. máximo 2GB por agente) y cuotas de CPU para evitar que un contenedor acapare la Raspberry Pi 5 y cause una denegación de servicio local.
* **Redes Virtuales Aisladas:** Creación de redes internas (ej. `agent_network`) donde los contenedores se comunican sin exposición al exterior. Solo el orquestador o API Gateway expone puertos.
* **Manejo de Secretos:** Uso de `docker secrets` para inyectar credenciales (como las llaves de RustFS/S3) directamente en memoria (tmpfs), sin guardarlas en variables de entorno o archivos en disco.
* **Volúmenes Cifrados:** Cifrado en reposo para los volúmenes de datos (`microdatos`, `macrodatos`) y registros (logs), asegurando la protección de la información estadística y geográfica.
* **Políticas de Reinicio:** Configuración de `restart: unless-stopped` para resiliencia ante fallos del servicio o reinicios de la Raspberry Pi.

## 3. Escaneo de Vulnerabilidades
Se integrará herramientas como **Trivy** en las canalizaciones de CI/CD para escanear las imágenes base (ej. RustFS) antes del despliegue, asegurando que no existan vulnerabilidades críticas (CVEs) conocidas en las capas de los contenedores.