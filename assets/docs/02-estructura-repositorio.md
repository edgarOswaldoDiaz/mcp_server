# 2. Estructura del Repositorio y Arquitectura

El proyecto está diseñado bajo el principio de **Separación de Responsabilidades**, dividiendo la lógica de negocio de la capa de transporte MCP y los recursos del repositorio.

```text
mcp_server/
├── assets/                     # Archivos estáticos, recursos e imágenes de soporte
│   └── docs/                   # Módulos de documentación del proyecto
├── config/                     # Configuraciones del proyecto (logging, etc.)
├── deployment/                 # Docker Compose y Dockerfiles de despliegue[cite: 11]
│   ├── compose/
│   │   └── docker-compose.yml
│   └── docker/
│       ├── Dockerfile.mcp
│       └── Dockerfile.tests
├── scripts/                    # Scripts de generación de claves JWT y tokens de prueba[cite: 11]
├── src/                        # Código fuente del proyecto[cite: 11]
│   ├── common/                 # Módulos transversales (configuración y logs)
│   └── mcp/
│       ├── client/             # Cliente de verificación interno
│       ├── server/             # Capa de transporte MCP y registro de endpoints
│       │   ├── auth.py
│       │   ├── main.py
│       │   ├── prompts.py
│       │   ├── resources.py
│       │   └── tools.py        # Registro de decoradores @mcp.tool
│       └── services/           # Lógica de negocio totalmente desacoplada
│           ├── calculator_service.py
│           ├── minio_service.py # Servicio de lectura de almacenamiento MinIO
│           └── system_service.py
├── tests/                      # Suite de pruebas unitarias e integración[cite: 11]
├── .gitlab-ci.yml              # Pipeline de Integración Continua (CI/CD)[cite: 11]
├── pytest.ini                  # Configuración del ejecutor de pruebas pytest
└── requirements.txt            # Dependencias del proyecto en Python