# 3.4 Gobernanza empresarial de MCP

La gobernanza empresarial de MCP es el marco operativo completo para gestionar qué servidores MCP existen en su organización, quién puede acceder a ellos, qué se les permite hacer y qué se registra cuando se utilizan.

- **Alcance:** Todos los servidores MCP. Esto incluye servidores internos construidos por equipos de producto, servidores ejecutándose en pipelines de CI/CD y cualquier cosa que un desarrollador haya configurado localmente en su IDE.
- **Mecanismo:** Una pasarela centralizada entre todos los clientes y todos los servidores MCP. La pasarela aplica las políticas. Los servidores MCP individuales no implementan sus propios controles de acceso, lo que hace que este enfoque sea escalable a través de cientos de servidores.
- **Resultado:** Cada invocación de herramienta es autorizada contra una identidad verificada y registrada en un formato estructurado y consultable que resiste la revisión de cumplimiento y la investigación de incidentes.

## Los Cuatro Pilares de la Gobernanza Empresarial de MCP

Un marco completo de gobernanza empresarial de MCP requiere cuatro capacidades que funcionan en conjunto: un catálogo centralizado, controles de acceso basados en identidad, registro de auditoría estructurado y aplicación de políticas en tiempo real. Cada una depende de las otras.

### Cuatro Pilares: Función Principal y Cobertura de Cumplimiento

| Pilar | Función principal | Cobertura de cumplimiento |
|---|---|---|
| 1. Catálogo centralizado | Registro único de servidores MCP aprobados con metadatos, propietario, estado de aprobación y alcance de acceso | Respalda la documentación de riesgo de proveedores y ayuda a prevenir el despliegue de herramientas no autorizadas (shadow tools) |
| 2. SSO y RBAC | Acceso basado en identidad mediante el IdP empresarial; permisos a nivel de herramienta aplicados en la pasarela | Respalda los requisitos de control de acceso de HIPAA; se alinea con SOC2 CC6; respalda los principios de responsabilidad de GDPR |
| 3. Registro de auditoría estructurado | Log JSON a prueba de manipulaciones por cada llamada a herramienta: quién llama, herramienta, argumentos, respuesta, decisión de política, latencia | Respalda prácticas de retención de auditoría alineadas con las expectativas de HIPAA; respalda la generación de evidencia de auditoría SOC2; respalda los requisitos de registro del Artículo 30 de GDPR |
| 4. Aplicación en tiempo real | Bloquear, enmascarar y limitar la tasa de solicitudes al momento de la invocación, antes de que la herramienta se ejecute | Ayuda a prevenir accesos no autorizados antes de la ejecución y respalda los flujos de respuesta a incidentes |

---
## Referencias

> Dubey, A. (Septiembre 11, 2026). *Enterprise MCP Governance*. TrueFoundry. https://www.truefoundry.com/es/blog/enterprise-mcp-governance-control-audit-secure-mcp-server-access
