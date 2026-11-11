# 8. Despliegue con Docker y CI/CD

Este documento describe la estrategia de empaquetado, orquestación en contenedores independientes y el pipeline de integración continua para el **Servidor MCP**.

## 1. Empaquetado de Contenedores (`Dockerfile.mcp`)

El servidor corre de forma totalmente independiente utilizando una imagen basada en Python que instala las dependencias de datos (`boto3`, `pandas`, `geopandas`) y expone el servicio FastMCP en el puerto `8000`.

## 2. Red Externa e Interoperabilidad

Para conectarse con otros contenedores (como el Agente de IA), el contenedor del servidor se vincula a una red Docker externa previamente creada en el host:

```
# Crear la red compartida en el host
docker network create mcp-interop-network

# Desplegar el servicio en segundo plano
cd deployment/compose
docker compose up -d --build mcp-server
```

## 3. Pipeline CI/CD en GitLab (`.gitlab-ci.yml`)

El ciclo de integración continua automatiza las siguientes fases en GitLab CI:

1. **Linting:** Verifica sintaxis y estándar de código Python.
2. **Testing:** Construye la imagen `Dockerfile.tests` y ejecuta `pytest` en un contenedor aislado.
3. **Build:** Compila la imagen de producción `Dockerfile.mcp` y la publica en el registro de contenedores.