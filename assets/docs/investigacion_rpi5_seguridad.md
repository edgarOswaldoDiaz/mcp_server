# Optimización de SO y Hardening de Contenedores para Raspberry Pi 5 (16GB)

**Fecha de Avance:** 9 de noviembre de 2026  
**Rol:** Seguridad de Persistencia y Contenedores  



## 1. Sistema Operativo y Kernel Optimizado

Para sacarle el máximo provecho a los 16GB de RAM de la Raspberry Pi 5 (arquitectura ARM64), descartamos por completo el uso de sistemas operativos de escritorio. Toda la memoria debe destinarse a los agentes computacionales y a los procesos de ciencia de datos.

* **Sistema Operativo Recomendado:** Alpine Linux o Ubuntu Server 24.04 LTS en su versión mínima.
* **Optimización a Nivel de Kernel:** Habilitación de `cgroups v2` (Control Groups) para un control estricto de CPU/RAM y `namespaces` para aislamiento de procesos. Desactivación de módulos innecesarios a nivel de hardware (Bluetooth, Wi-Fi al usar Ethernet y controladores de audio) para minimizar la superficie de ataque.



## 2. Hardening (Endurecimiento) de Docker

Para cumplir con las normativas de seguridad, la arquitectura contenerizada implementa las siguientes reglas de protección:

* **Modo Rootless:** Ejecución del demonio de Docker sin privilegios de superusuario (`root`). Si un contenedor se ve comprometido, el atacante no obtendrá permisos de administración sobre la Raspberry Pi.
* **Límites de Recursos (Prevención DoS):** Asignación de cuotas de CPU y límites estrictos de memoria (máximo 2GB por agente) para evitar saturación del sistema o ataques de Denegación de Servicio local.
* **Redes Virtuales Aisladas:** Implementación de redes internas (`Internal: true`) tipo búnker. Los contenedores se comunican internamente sin exposición a internet; solo los orquestadores autorizados exponen puertos.
* **Manejo Seguro de Secretos:** Uso de `docker secrets` para inyectar credenciales (como llaves de RustFS/S3) directamente en memoria volátil (`tmpfs`), evitando almacenar contraseñas en variables de entorno o archivos de disco.
* **Volúmenes Cifrados:** Cifrado en reposo para los volúmenes de almacenamiento de datos y registros (*logs*), garantizando la integridad de la información estadística y geográfica.
* **Alta Disponibilidad:** Configuración de la política `restart: unless-stopped` para permitir la autorrecuperación de los servicios ante cortes de energía o reinicios de la tarjeta.



## 3. Escaneo de Vulnerabilidades

Integración de herramientas como **Trivy** dentro de las canalizaciones de CI/CD para auditar las imágenes base (como RustFS) antes de su despliegue, previniendo la introducción de vulnerabilidades conocidas (CVEs) en el entorno de producción.