# 1. Visión General del Proyecto

## ¿Qué es el Model Context Protocol (MCP)?
El **Model Context Protocol (MCP)** es un estándar abierto que permite conectar asistentes de Inteligencia Artificial (LLMs) con fuentes de datos externas, APIs y herramientas locales de forma segura, estructurada y controlada.

## Propósito de este Servidor
Este proyecto actúa como una plantilla de grado de producción (*Enterprise Ready*) estructurada para integrar cualquier servicio de negocio con asistentes de lenguaje. 

Actualmente, el servidor proporciona:
* **Cálculos e información del sistema:** Herramientas de diagnóstico y cómputo matemático.
* **Integración S3 con MinIO:** Herramientas para la consulta y extracción segura de archivos sintéticos y análisis de datos en formatos **JSON**, **Parquet** y **GeoParquet**.
* **Control de Seguridad:** Validación de permisos por alcance de tokens (`auth=require_scopes`) y segregación de accesos evitando el uso de cuentas *root*.