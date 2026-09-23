# MCP Server - Guía Completa de Arquitectura e Implementación

Este proyecto implementa un servidor completo de **Model Context Protocol (MCP)** en Python. Está diseñado bajo una arquitectura limpia, extensible y testeable, listo para conectarse con clientes de IA como **Claude Desktop**, **Cursor** o **VS Code**, o desplegarse mediante contenedores **Docker**.

---

##  Tabla de Contenidos

1. [Visión General del Proyecto](#1-visión-general-del-proyecto)
2. [Estructura del Repositorio](#2-estructura-del-repositorio)
3. [Capacidades MCP Implementadas](#3-capacidades-mcp-implementadas)
4. [Flujo de Ejecución e Instalación](#4-flujo-de-ejecución-e-instalación)
5. [Integración con Clientes MCP (Claude Desktop)](#5-integración-con-clientes-mcp-claude-desktop)
6. [Pruebas Automatizadas y Calidad](#6-pruebas-automatizadas-y-calidad)
7. [Despliegue con Docker y CI/CD](#7-despliegue-con-docker-y-cicd)
8. [Comparativa de Arquitectura](#8-comparativa-de-arquitectura)

---

## 1. Visión General del Proyecto

El **Model Context Protocol (MCP)** es un estándar abierto desarrollado para conectar asistentes de Inteligencia Artificial con fuentes de datos externas, APIs y herramientas locales de forma segura y estandarizada.

Este proyecto actúa como una plantilla de grado de producción (*Enterprise Ready*) para integrar cualquier servicio de negocio (por ejemplo, consultas de datos del INEGI, herramientas del sistema o cálculos) con asistentes LLM.

---

## 2. Estructura del Repositorio

El código sigue el principio de **Separación de Responsabilidades**, dividiendo los servicios de negocio de la capa de protocolo MCP:

```text
mcp-server/
├── config/
│   └── logging.yml              # Configuración centralizada de logs
├── deployment/
│   ├── compose/
│   │   └── docker-compose.yml   # Orquestación de contenedores
│   └── docker/
│       ├── Dockerfile.mcp       # Contenedor principal del servidor
│       └── Dockerfile.tests     # Contenedor para ejecución de pruebas
├── src/
│   ├── common/                  # Módulos transversales (configuración, logging)
│   │   ├── config.py
│   │   └── logging.py
│   └── mcp/
│       ├── client/              # Cliente de prueba interno para validación manual
│       │   └── test_client.py
│       ├── server/              # Capa de transporte y protocolo MCP (FastMCP)
│       │   ├── main.py          # Creación e inicio del servidor
│       │   ├── metadata.py      # Metadatos del proyecto (nombre, versión)
│       │   ├── prompts.py       # Registro de Prompts
│       │   ├── resources.py     # Registro de Recursos
│       │   └── tools.py         # Registro de Herramientas
│       └── services/            # Lógica de negocio desacoplada
│           ├── calculator_service.py
│           └── system_service.py
├── tests/                       # Suite de pruebas automatizadas
│   ├── integration/             # Pruebas de integración de protocolo
│   │   ├── conftest.py
│   │   └── mcp/
│   │       └── test_mcp_server.py
│   └── unit/                    # Pruebas unitarias de servicios y servidor
│       ├── test_calculator_service.py
│       ├── test_prompts.py
│       ├── test_resources.py
│       ├── test_server.py
│       ├── test_system_service.py
│       └── test_tools.py
├── .gitlab-ci.yml               # Pipeline Integración Continua (CI/CD)
├── pytest.ini                   # Configuración de runner pytest
└── requirements.txt             # Dependencias del entorno
```

---

## 3. Capacidades MCP Implementadas

El servidor registra dinámicamente las tres primitivas fundamentales de la especificación MCP utilizando el SDK `FastMCP`:

###  Tools (Herramientas)
Funciones ejecutables por el modelo de lenguaje:
* **`get_system_status`**: Retorna el estado de salud y versión del servidor MCP.
* **`echo`**: Retorna el mensaje recibido (útil para pruebas de conectividad).
* **`add`**: Suma dos números enteros de forma segura llamando al servicio de cálculo.

###  Resources (Recursos)
Datos contextuales expuestos como URIs que el LLM puede consultar:
* **`config://server`**: Expone en formato JSON la configuración actual del servidor (nombre, versión, entorno).

###  Prompts (Plantillas de Contexto)
Plantillas predefinidas que guían las respuestas del LLM:
* **`system_diagnostic`**: Genera una instrucción estructurada para diagnosticar conectividad, herramientas y recursos disponibles.

---

## 4. Flujo de Ejecución e Instalación

### Requisitos Previos
* **Python 3.10+**
* `pip` o `uv` instalado.

### Paso 1: Clonar e instalar dependencias

```bash
# Clonar repositorio
git clone https://github.com/edgarOswaldoDiaz/mcp_server/tree/EquipoA-MCPServer
cd mcp-server

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Iniciar el servidor MCP

El servidor se ejecuta por defecto exponiendo un transporte HTTP/SSE en `0.0.0.0:8000`:

```bash
python -m src.mcp.server.main
```

### Paso 3: Probar el servidor con el cliente integrado

En otra ventana de la terminal (con el servidor en ejecución), puedes correr el cliente de verificación:

```bash
python -m src.mcp.client.test_client
```

---

## 5. Integración con Clientes MCP (Claude Desktop)

Para que un cliente MCP como **Claude Desktop** reconozca y ejecute este servidor localmente, añade la siguiente configuración en tu archivo `claude_desktop_config.json`:

### Ubicación del archivo de configuración:
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### Configuración JSON (Modo Stdio / Python Ejecutable):

```json
{
  "mcpServers": {
    "mcp-server-inegi": {
      "command": "C:\\ruta\\a\\tu\\proyecto\\venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "src.mcp.server.main"
      ],
      "cwd": "C:\\ruta\\a\\tu\\proyecto\\mcp-server"
    }
  }
}
```

---

## 6. Pruebas Automatizadas y Calidad

El proyecto incluye pruebas completas con `pytest` y `pytest-asyncio`.

```bash
# Ejecutar la totalidad de las pruebas (Unitarias e Integración)
pytest

# Ejecutar únicamente pruebas unitarias
pytest tests/unit

# Ejecutar únicamente pruebas de integración
pytest tests/integration
```

---

## 7. Despliegue con Docker y CI/CD

### Despliegue con Docker Compose
Puedes levantar el servidor en segundo plano junto con el contenedor de pruebas de integración:

```bash
docker-compose -f deployment/compose/docker-compose.yml up --build
```

### Integración Continua (CI/CD)
El archivo `.gitlab-ci.yml` define automáticamente tres etapas:
1. **Linting / Format Check**: Validación de estilo del código.
2. **Testing**: Ejecución de las pruebas unitarias e integrales dentro de un entorno Dockerizado (`Dockerfile.tests`).
3. **Build**: Generación de la imagen del contenedor lista para producción (`Dockerfile.mcp`).

---

## 8. Comparativa de Arquitectura

| Aspecto | Script Básico MCP | Implementación de este Repositorio |
| :--- | :--- | :--- |
| **Organización** | Un solo archivo monolítico (`server.py`). | Estructura por capas (`services/`, `server/`, `common/`). |
| **Primitivas MCP** | Solo implementa *Tools*. | Implementa *Tools*, *Resources* y *Prompts*. |
| **Manejo de Lógica** | Código directo dentro del decorador MCP. | Invocación de servicios desacoplados (`calculator_service`, etc.). |
| **Pruebas** | Pruebas manuales en consola. | Suite completa con `pytest` y cliente de integración implícito. |
| **Contenerización** | Ninguna o básica. | Multi-stage Dockerfiles + `docker-compose` + CI/CD configurado. |
