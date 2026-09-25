# Reporte de Validación y Aseguramiento de Calidad (QA)

## 1. Resumen Ejecutivo

Este documento muestra como se llevó a cabo la ejecución de la suite de pruebas automatizadas, que valida la conectividad, la seguridad perimetral, la autenticación por token y la resiliencia operativa del entorno contenerizado bajo el protocolo A2A. Las pruebas se ejecutaron sobre un entorno de contenedores Docker sincronizado.

---

## 2. Indicador Clave de Rendimiento (KPI 1)

El KPI 1 evalúa la tasa de éxito en las pruebas automatizadas de integración y conectividad de los componentes del Protocolo A2A.

- **Fórmula de Cálculo:**
  $$\text{KPI 1} = \left( \frac{\text{Pruebas Exitosas}}{\text{Pruebas Ejecutadas}} \right) \times 100$$
- **Meta Institucional Requerida:** $\ge 90\%$
- **Total de Pruebas Ejecutadas:** $19$
- **Total de Pruebas Exitosas:** $19$
- **Resultado Obtenido:** **100%**

---

## 3. Matriz de Casos de Prueba Validados

La suite implementada en la ruta `tests/` cubre los siguientes dominios funcionales:

| ID de Módulo      | Categoría        | Componente Evaluado                                              | Endpoint Objetivo                      | Estatus  |
| :---------------- | :--------------- | :--------------------------------------------------------------- | :------------------------------------- | :------- |
| **TC-01 a TC-03** | **Conectividad** | Descubrimiento de identidad y estructura del Agent Card          | `GET /.well-known/agent-card.json`     | **PASS** |
| **TC-04 a TC-07** | **Integración**  | Envío de mensajes JSON-RPC 2.0 y flujos de Tareas                | `POST /a2a/rpc`, `GET /a2a/tasks/{id}` | **PASS** |
| **TC-08 a TC-16** | **Seguridad**    | Validación perimetral, esquemas Bearer y rechazo de credenciales | `POST /a2a/rpc`, `GET /a2a/tasks/{id}` | **PASS** |
| **TC-17 a TC-19** | **Resiliencia**  | Control de excepciones ante métodos no soportados y payloads     | `POST /a2a/rpc`                        | **PASS** |

---

## 4. Instrucciones de Replicabilidad Técnica

Para replicar la ejecución de la suite de pruebas:

1. Clonar el repositorio y posicionarse en la rama de trabajo:

   ```bash
   git clone https://github.com/edgarOswaldoDiaz/mcp_server.git
   cd mcp_server
   git checkout equipo-b-a2a
   ```

2. Construir y levantar el entorno contenerizado mediante Docker Compose:

   ```bash
   docker compose up -d --build
   ```

3. Ejecutar la suite automatizada de validación:
   ```bash
   python -m pytest tests/ -v
   ```
