## Docker como Contenedor para Servidores MCP

### Puntos de Dolor en la Adopción de MCP

Antes de la llegada de soluciones como Docker, la adopción de MCP enfrentaba una serie de problemas recurrentes para los equipos de desarrollo:

* **Entorno de ejecución (*runtime*):** poner en marcha un servidor MCP resultaba pesado, ya que los *runtimes* estándar dependen de versiones específicas de Python o Node.js. Combinar varias herramientas implicaba gestionar manualmente esas versiones, además de las dependencias adicionales que cada servidor pudiera requerir.
* **Seguridad:** otorgarle a un LLM acceso directo para ejecutar software en el sistema anfitrión resultaba inaceptable fuera de entornos puramente experimentales, ya que una alucinación o una salida incorrecta del modelo podía causar daños significativos. A esto se sumaba que a los usuarios se les pedía configurar datos sensibles en archivos JSON de texto plano: un archivo de configuración de MCP concentra toda la información necesaria para que el agente actúe en nombre del usuario, pero, por la misma razón, también concentra todo lo que un atacante necesitaría para comprometer sus cuentas.
* **Descubribilidad:** aunque las herramientas ya existían, no había un lugar único y confiable para encontrar los mejores servidores MCP; comenzaban a surgir *marketplaces*, pero los desarrolladores seguían teniendo que buscar por su cuenta buenas fuentes de herramientas. Además, a medida que se acumulan más servidores y herramientas conectadas, es fácil saturar al LLM, lo que deriva en el uso de herramientas incorrectas y peores resultados.
* **Confianza:** dado que las herramientas son ejecutadas por el LLM en nombre del desarrollador, resulta crítico poder confiar en quién publica cada servidor MCP. El panorama actual de publicadores se asemeja a una auténtica "fiebre del oro", lo que lo vuelve vulnerable a ataques a la cadena de suministro provenientes de autores no confiables.

### Docker como Runtime para MCP

Docker ofrece un entorno de ejecución probado para estabilizar el contexto en el que corren las herramientas. En lugar de gestionar múltiples instalaciones de Node o Python, usar servidores MCP "dockerizados" permite que cualquier persona con el motor de Docker instalado pueda ejecutarlos sin fricción.

Además, Docker aporta aislamiento tipo *sandbox* para las herramientas, de modo que un comportamiento indeseado del LLM no pueda dañar la configuración del sistema anfitrión. Por ejemplo, el modelo no tiene acceso al sistema de archivos del host, a menos que ese contenedor MCP lo permita de forma explícita.

### La Puerta de Enlace MCP (MCP Gateway)

Para que un LLM pueda operar de manera autónoma, necesita ser capaz de descubrir y ejecutar herramientas por sí mismo, algo casi imposible de lograr gestionando manualmente decenas de servidores MCP individuales: cada vez que se agrega una herramienta nueva, hay que actualizar el archivo de configuración y recargar el cliente MCP correspondiente.

La alternativa que propone Docker es usar un único servidor MCP (el propio Docker) que funcione como puerta de enlace (*gateway*) hacia un conjunto dinámico de herramientas contenerizadas. Esta dinamismo se logra mediante una interfaz sencilla en Docker Desktop, donde es posible mantener y modificar la lista de herramientas que la puerta de enlace expone, sin tener que tocar ningún archivo de configuración. Así, los usuarios pueden habilitar cientos de servidores dockerizados en sus clientes MCP con solo "conectarse" a este servidor gateway.

### El Catálogo MCP

De forma similar a Docker Hub, el Catálogo MCP de Docker funciona como un punto centralizado y confiable para que los desarrolladores descubran herramientas. 

Para quienes desarrollan herramientas, ese mismo catálogo se convierte en un canal de distribución clave: una manera de llegar a nuevos usuarios y garantizar compatibilidad con plataformas como Claude, Cursor, OpenAI y VS Code.

El catálogo es, en concreto, una colección curada de servidores MCP verificados, empaquetados como imágenes de Docker y distribuidos a través de Docker Hub. Resuelve los problemas más comunes de ejecutar servidores MCP de forma local: conflictos de entorno, complejidad de configuración y riesgos de seguridad. 

Al agregar servidores a un perfil, estos se seleccionan precisamente desde este catálogo, y cada servidor corre como un contenedor aislado, lo que garantiza su portabilidad y consistencia entre distintos entornos.

El catálogo incluye distintos tipos de contenido:

* **Servidores verificados:** todos cuentan con versionado, procedencia completa y metadatos de tipo SBOM (lista de materiales de software).
* **Herramientas de socios:** servidores provistos por partners de confianza, como New Relic, Stripe o Grafana.
* **Servidores construidos por Docker:** servidores de ejecución local, creados y firmados digitalmente por Docker para reforzar su seguridad.
* **Servicios remotos:** servidores alojados en la nube que se conectan a servicios externos como GitHub, Notion o Linear.

Según dónde se ejecutan, los servidores del catálogo se dividen en dos categorías:

* **Servidores locales:** corren como contenedores en la propia máquina del usuario. Una vez descargados, funcionan sin conexión a internet, ofrecen un rendimiento predecible y garantizan privacidad total de los datos. Docker construye y firma todos los servidores locales del catálogo.
* **Servidores remotos:** se ejecutan en la infraestructura del propio proveedor del servicio y se conectan a sistemas externos. Muchos de ellos utilizan autenticación OAuth, la cual es gestionada automáticamente por el navegador a través del MCP Toolkit.

### Docker Secrets

Para trasladar de forma segura tokens de acceso y otros secretos entre contenedores, Docker desarrolló una función dentro de Docker Desktop dedicada a la gestión de secretos. Una vez configurados, estos secretos solo quedan expuestos al proceso del contenedor del servidor MCP correspondiente, es decir, no aparecen ni siquiera al inspeccionar el contenedor en ejecución. Mantener los secretos acotados exclusivamente a las herramientas que realmente los necesitan elimina el riesgo de que grandes filtraciones de datos ocurran simplemente por dejar archivos de configuración de MCP expuestos.

### Docker MCP Toolkit

El Docker MCP Toolkit es la interfaz de administración integrada en Docker Desktop que permite configurar, gestionar y ejecutar servidores MCP en contenedores (organizados mediante perfiles) y conectarlos con agentes de IA. 

Ofrece configuraciones predeterminadas seguras, una puesta en marcha sencilla y compatibilidad con un ecosistema creciente de clientes basados en LLM, siendo la vía más rápida para pasar del descubrimiento de una herramienta MCP a su ejecución local.

**Requisitos previos:**

* Descargar e instalar la versión más reciente de Docker Desktop.
* Abrir la configuración de Docker Desktop y acceder a la sección de funciones Beta.
* Habilitar el Docker MCP Toolkit y aplicar los cambios.

**Flujo de configuración inicial:**

1. **Crear un perfil:** el espacio de trabajo donde se organizan los servidores.
2. **Agregar servidores MCP al perfil:** seleccionando herramientas directamente desde el catálogo.
3. **Conectar clientes:** vinculando las aplicaciones de IA al perfil creado.
4. **Verificar las conexiones:** comprobando que todo funcione correctamente.

Una vez completada esta configuración, las aplicaciones de IA conectadas pueden utilizar todos los servidores incluidos en el perfil correspondiente.

Para crear un perfil, dentro de Docker Desktop se accede a la pestaña de Perfiles del MCP Toolkit, se selecciona la opción de crear uno nuevo, se le asigna un nombre descriptivo (por ejemplo, "Desarrollo frontend") y, de forma opcional, se pueden añadir servidores y clientes en ese mismo momento o hacerlo más adelante.

Para agregar servidores, se navega a la pestaña del Catálogo, se exploran las herramientas disponibles y se seleccionan las que se desean incorporar, indicando si deben añadirse a un perfil existente o a uno nuevo. Algunos servidores requieren una configuración adicional obligatoria antes de poder utilizarse, lo cual se indica mediante un distintivo visible junto a su nombre.

Para conectar un cliente, se accede a la pestaña de Clientes del Toolkit, se localiza la aplicación deseada en la lista y se selecciona la opción de conexión correspondiente. Si el cliente no aparece listado, también es posible conectarlo manualmente configurándolo para ejecutar la puerta de enlace mediante el transporte *stdio*, indicando el perfil a utilizar, por ejemplo:

```
docker mcp gateway run --profile my_profile
```

En el caso de clientes que usan un archivo JSON para definir sus servidores MCP, esto puede reflejarse con una entrada similar a:

```json
{
  "servers": {
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "run", "--profile", "my_profile"],
      "type": "stdio"
    }
  }
}
```

### Perfiles MCP

Los perfiles resuelven un problema práctico: sin ellos, sería necesario configurar los servidores por separado para cada aplicación de IA utilizada, y cada cambio en las herramientas disponibles implicaría actualizar manualmente cada cliente (Claude Desktop, VS Code, Cursor, entre otros). Los perfiles centralizan esa configuración en colecciones con nombre.

Un perfil es, en esencia, una colección nombrada de servidores MCP junto con sus configuraciones y ajustes. Los servidores se seleccionan desde el Catálogo MCP y se agregan a los distintos perfiles, que actúan como cajas de herramientas organizadas según la tarea o el proyecto. 

Por ejemplo, un perfil de "desarrollo web" podría incluir servidores de GitHub, Playwright y bases de datos, mientras que un perfil de "análisis de datos" podría incluir servidores de hojas de cálculo, APIs y visualización.

**Características principales de los perfiles:**

* Cada perfil mantiene una colección aislada de servidores y configuraciones, independiente de los demás perfiles. Es posible crear tantos perfiles como se necesiten, cada uno con solo los servidores relevantes para su contexto.
* Las credenciales OAuth son una excepción a este aislamiento: se comparten entre todos los perfiles. Si se requiere usar cuentas distintas para proyectos diferentes, es necesario revocar y volver a autorizar el acceso al cambiar de perfil.
* Distintas aplicaciones de IA pueden conectarse a distintos perfiles: al conectar un cliente, se especifica qué perfil debe utilizar, por lo que, por ejemplo, Claude Desktop y VS Code pueden acceder a colecciones diferentes de servidores si así se requiere.
* Los perfiles pueden compartirse con un equipo, subiéndolos a un registro para que otros miembros descarguen la misma colección de servidores y configuraciones.

**Gestión de perfiles:** desde la pestaña de Perfiles en Docker Desktop es posible crear un perfil nuevo (asignándole un nombre y, opcionalmente, servidores y clientes desde el inicio), revisar sus detalles (ya sea el resumen de servidores, secretos y clientes conectados, o el listado de herramientas disponibles con la posibilidad de activarlas o desactivarlas individualmente), y eliminarlo cuando ya no se necesite. Eliminar un perfil borra de forma irreversible todas sus configuraciones y actualiza la configuración de los clientes que lo usaban.

Cuando se ejecuta la puerta de enlace MCP o se conecta un cliente sin especificar un perfil de forma explícita, Docker MCP utiliza automáticamente un perfil llamado "predeterminado" (o una configuración vacía si este no existe). Es posible indicar explícitamente un perfil distinto mediante el indicador correspondiente al ejecutar la puerta de enlace, por ejemplo:

```
docker mcp gateway run --profile web-dev
```

---

## Referencias

> Docker. (2025, Abril 25). *How to build and deliver an MCP server for production*. Docker Blog. https://www.docker.com/blog/build-to-prod-mcp-servers-with-docker/

> Docker. *Catálogo Docker MCP*. Docker Docs. https://docs.docker.com/ai/mcp-catalog-and-toolkit/catalog/

> Docker. *Comience a usar Docker MCP Toolkit*. Docker Docs. https://docs.docker.com/ai/mcp-catalog-and-toolkit/get-started/

> Docker. *Perfiles MCP*. Docker Docs. https://docs.docker.com/ai/mcp-catalog-and-toolkit/profiles/
