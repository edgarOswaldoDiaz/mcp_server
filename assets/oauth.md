# 3.3 OAuth 2.0

## ¿Qué es OAuth 2.0?

OAuth 2.0 es el protocolo estándar de la industria para la autorización. Define flujos de autorización específicos para aplicaciones web, aplicaciones de escritorio, dispositivos móviles y dispositivos domésticos. Esta especificación y sus extensiones continúan desarrollándose dentro del Grupo de Trabajo OAuth de la IETF.

## Tokens de Acceso OAuth

Un token de acceso OAuth es una cadena de caracteres que el cliente OAuth utiliza para realizar solicitudes al servidor de recursos. No existe un formato obligatorio para estos tokens; en la práctica, distintos servidores OAuth han adoptado formatos muy variados.

Los tokens de acceso pueden clasificarse en dos tipos:

* **Tokens de portador (*bearer tokens*):** cualquiera que posea el token puede usarlo.
* **Tokens con restricción de remitente:** exigen que el cliente OAuth demuestre, de alguna manera, que posee una clave privada asociada, de modo que el token por sí solo no resulta utilizable por un tercero que lo intercepte.

Existen tres propiedades fundamentales para el modelo de seguridad de OAuth en torno a los tokens de acceso:

* No deben ser leídos ni interpretados por el cliente OAuth, ya que este no es su destinatario previsto.
* No transmiten la identidad del usuario ni ninguna otra información sobre él al cliente OAuth.
* Solo deben utilizarse para realizar solicitudes al servidor de recursos; de igual forma, los tokens de identidad (*ID tokens*) no deben usarse para este fin.

## Tokens de Actualización OAuth (*Refresh Tokens*)

Un token de actualización es una cadena de caracteres que el cliente OAuth puede usar para obtener un nuevo token de acceso sin necesidad de interacción del usuario.

Tanto los clientes públicos como los confidenciales pueden utilizar tokens de actualización, aunque el nivel de riesgo difiere entre ambos:

* Si se roba un token de actualización emitido a un **cliente público**, un atacante puede suplantar al cliente y usar el token sin ser detectado. Es posible mitigar este riesgo vinculando el token de actualización a la instancia específica del cliente público mediante DPoP.
* Los **clientes confidenciales** deben autenticarse ante el servidor de autorización para poder usar su token de actualización, lo que reduce el riesgo de robo para este tipo de cliente.

Un token de actualización no debe permitir que el cliente obtenga acceso más allá del alcance de la concesión original. Su función principal es permitir que los servidores de autorización utilicen tokens de acceso de corta duración, sin requerir intervención del usuario cada vez que uno de estos tokens expira.

## Ámbitos de OAuth (*Scopes*)

El ámbito (*scope*) es el mecanismo de OAuth 2.0 que permite limitar el acceso de una aplicación a la cuenta de un usuario. Una aplicación puede solicitar uno o más ámbitos, los cuales se presentan al usuario en la pantalla de consentimiento; el token de acceso emitido quedará limitado a los ámbitos efectivamente concedidos.

La especificación permite que el servidor de autorización o el propio usuario modifiquen los ámbitos otorgados respecto a los solicitados originalmente, aunque en la práctica son pocos los servicios que implementan esta posibilidad. OAuth no define valores específicos para los ámbitos, ya que estos dependen en gran medida de la arquitectura interna y las necesidades particulares de cada servicio.

## Beneficios de OAuth

OAuth permite otorgar a las aplicaciones acceso temporal a datos y recursos protegidos mediante tokens de acceso que:

* Tienen una duración limitada en el tiempo.
* Son revocables.
* No requieren compartir las credenciales del usuario con terceros.
* Permiten otorgar acceso específico a determinados datos o recursos.
* Reducen la necesidad de usar múltiples contraseñas e inicios de sesión distintos entre servicios.

---

## ¿Por Qué OAuth Resulta Especialmente Beneficioso al Usar MCP?

Los servidores MCP facilitan la integración entre los sistemas basados en modelos de lenguaje (LLM) y las aplicaciones y datos con los que estos interactúan. Sin embargo, esta integración ha traído consigo diversos riesgos de seguridad, que van desde acciones no deseadas de agentes de IA mal orientados, hasta riesgos derivados directamente de servidores MCP maliciosos o con un diseño deficiente.

OAuth aborda buena parte de estas deficiencias de seguridad presentes en los entornos MCP: delimita tanto el acceso de los agentes de IA a los datos como la duración de ese acceso, utiliza un sistema de tokens en lugar de compartir credenciales directamente, y garantiza un flujo de autenticación y autorización sólido dentro de estos entornos.

Al implementar OAuth en servidores MCP, es importante tener en cuenta que la propia especificación de MCP incluye directivas específicas sobre cómo debe funcionar OAuth en este contexto, entre ellas:

* Los clientes MCP **deben** implementar la función de clave de prueba para el intercambio de códigos (**PKCE**).
* Todos los puntos finales del servidor de autorización deben servirse exclusivamente a través de **HTTPS**.

### ¿Cómo Funciona el Flujo de OAuth en MCP?

1. El cliente MCP envía una solicitud de acceso al servidor MCP.
2. El servidor MCP responde con un estado **401 No autorizado**.
3. El cliente obtiene los metadatos del servidor, que incluyen los detalles necesarios para la autorización.
4. El usuario otorga su consentimiento para que el servidor de autorización le proporcione un token de acceso al cliente.
5. El servidor de autorización entrega el token de acceso al cliente.
6. El cliente repite la solicitud inicial de acceso al servidor MCP, esta vez incluyendo el token de acceso, y se le concede el acceso al recurso protegido.

### Roles dentro del Flujo OAuth en MCP

* **Cliente MCP:** actúa como un cliente OAuth 2.1, realizando solicitudes de acceso a recursos protegidos en nombre del propietario del recurso (el usuario).
* **Servidor MCP:** actúa como un servidor de recursos OAuth 2.1, otorgando acceso a los recursos protegidos cuando el cliente presenta un token válido y completa correctamente el proceso PKCE.
* **Servidor de autorización:** emite los tokens de acceso que el cliente MCP utiliza para acceder a los recursos protegidos a través del servidor MCP.
* **Propietario del recurso** (normalmente el usuario): autentica la solicitud con sus propias credenciales y otorga su consentimiento para que el servidor de autorización entregue tokens de acceso al cliente.

### Complejidad de la Implementación

Implementar OAuth dentro de los flujos de un servidor MCP resulta notoriamente complejo, al punto de que son frecuentes las publicaciones en foros de desarrolladores de servidores MCP pidiendo ayuda tras varios intentos fallidos de hacer funcionar correctamente su flujo de OAuth. Por esta razón, muchas organizaciones optan por utilizar una solución de autorización secundaria, o bien centralizar la autorización, la autenticación y la gestión de identidades a través de una puerta de enlace MCP (*MCP Gateway*).

## Cómo Agregar OAuth a Servidores MCP que no lo Soportan

Si se desea utilizar servidores MCP que no admiten OAuth de forma nativa, es posible recurrir a un *proxy* o a una puerta de enlace MCP para imponer el flujo de autorización entre los clientes y esos servidores. En esta configuración, la puerta de enlace MCP gestiona el flujo de autorización OAuth como parte de su función de mediar el tráfico, las solicitudes y las respuestas entre clientes y servidores MCP.

Centralizar los flujos de OAuth a través de una puerta de enlace ofrece varias ventajas:

* Flujos de OAuth confiables y consistentes en todos los servidores conectados.
* Registro integral de extremo a extremo a nivel empresarial, útil para observabilidad y resolución de problemas.
* Un punto único de mantenimiento y gestión para los flujos y tokens de OAuth.
* La posibilidad de asignar identidades distintas para el uso de cada servidor MCP, incluyendo identidades propias para los agentes de IA.
* Supervisión a nivel empresarial, con capacidad de monitorear y revocar tokens a gran escala.
* Un refuerzo general del proceso de OAuth y del almacenamiento de tokens y secretos.

---

## Referencias

> OAuth.net. (s.f.). *OAuth 2.0*. OAuth.net. https://oauth.net/2/

> OAuth.net. (s.f.). *Access Tokens*. OAuth.net. https://oauth.net/2/access-tokens/

> OAuth.net. (s.f.). *Refresh Tokens*. OAuth.net. https://oauth.net/2/refresh-tokens/

> OAuth.net. (s.f.). *Scope*. OAuth.net. https://oauth.net/2/scope/

> Taylor, J. (Agosto 18, 2025). *OAuth for MCP*. MCP Manager. https://mcpmanager.ai/blog/oauth-for-mcp/
