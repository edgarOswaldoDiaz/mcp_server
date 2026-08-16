# 2.2.1 SDK de Cliente — Python

## Introducción

El SDK oficial de Python para MCP (`mcp`) es la implementación de referencia mantenida por el proyecto Model Context Protocol. Provee la clase `Client`, el objeto central a través del cual una aplicación host se comunica con uno o varios servidores MCP.

Este SDK es la base sobre la que se construyen los clientes que después integran un LLM (por ejemplo, vía la API de Anthropic u Ollama) para decidir qué herramientas invocar.

## Requisitos del Sistema

| Requisito | Versión mínima |
|---|---|
| Sistema operativo | macOS o Windows (también funciona en Linux) |
| Python | Última versión estable |
| Gestor de paquetes | `uv` (recomendado) |
| SDK Python de MCP | 2.0.0 o superior|

`uv` es el gestor de entornos y paquetes recomendado por el proyecto MCP porque simplifica la creación de entornos virtuales y la gestión de dependencias en un solo comando.

## Instalación y Configuración del Proyecto

```bash
# Crear directorio del proyecto
uv init mcp-client
cd mcp-client

# Crear entorno virtual
uv venv

# Activar entorno virtual (macOS/Linux)
source .venv/bin/activate

# Instalar paquetes requeridos
uv add mcp anthropic python-dotenv

# Archivo principal
touch client.py
```

## Configuración de la Clave API
 
La forma de configurar el acceso al LLM depende de si se utiliza la API de Anthropic o un modelo servido localmente mediante Ollama.
 
### Con Anthropic
 
Se necesita una clave de API de Anthropic, obtenida desde la [consola de Anthropic](https://console.anthropic.com/settings/keys). Se crea un archivo `.env` para almacenarla:
 
```bash
echo "ANTHROPIC_API_KEY=your-api-key-goes-here" > .env
```
 
Y se agrega `.env` al `.gitignore` para evitar exponerla por accidente:
 
```bash
echo ".env" >> .gitignore
```
 
### Con Ollama
 
A diferencia de Anthropic, Ollama no requiere una clave de API: el modelo se ejecuta de forma local y se expone mediante una API REST en `http://localhost:11434` por defecto. Aun así, conviene definir esa dirección como variable de entorno para no dejarla escrita directamente en el código, especialmente si el servidor de Ollama corre en otra máquina de la red o en un puerto distinto al predeterminado.
 
Se crea un archivo `.env` para almacenar la configuración:
 
```bash
echo "OLLAMA_HOST=http://localhost:11434" > .env
```
 
Si el modelo requiere autenticación adicional (por ejemplo, si Ollama está expuesto detrás de un proxy o gateway con control de acceso), también puede agregarse una variable para ese token:
 
```bash
echo "OLLAMA_API_KEY=your-api-key-goes-here" >> .env
```
 
Al igual que en el caso anterior, se agrega `.env` al `.gitignore`:
 
```bash
echo ".env" >> .gitignore
```
 
**Diferencia clave:** mientras que con Anthropic la clave de API es obligatoria y se obtiene desde la consola del proveedor, con Ollama la variable de entorno es opcional en la mayoría de los casos, siendo indispensable únicamente si el servidor no corre en `localhost` con su configuración por defecto, o si se implementó una capa de autenticación adicional sobre él.

## El Objeto `Client`: Concepto Central

Un `Client` es el único objeto con el que el programa habla con un servidor MCP. Tiene **un ciclo de vida**: se construye, se entra a un bloque `async with`, y se llaman sus métodos.

```python
from mcp import Client
from mcp.server import MCPServer

mcp = MCPServer("Bookshop", instructions="Busca en el catálogo antes de recomendar un libro.")

@mcp.tool()
def search_books(query: str) -> str:
    """Busca en el catálogo por título o autor."""
    return f"Se encontraron 3 libros que coinciden con {query!r}."


async def main() -> None:
    async with Client(mcp) as client:
        print(client.server_info)
        print(client.server_capabilities)
        print(client.protocol_version)
```

Puntos clave:

* **No existe un par `connect()` / `close()`:** entrar al bloque `async with` conecta y negocia el protocolo; salir del bloque desconecta.
* Un `Client` **no se puede reutilizar** una vez que el bloque termina.
* Dentro del bloque, las propiedades de la conexión ya están disponibles: `server_info`, `server_capabilities`, `protocol_version`, `instructions`.

### Tipos de Transporte que Acepta `Client`

| Se le pasa a `Client(...)` | Transporte | Uso típico |
|---|---|---|
| Una instancia `MCPServer` | En memoria (sin subproceso, sin puerto) | Pruebas y desarrollo local |
| Un string URL (`"http://localhost:8000/mcp"`) | Streamable HTTP | Producción, servidores remotos |
| Un objeto transporte (ej. `stdio_client(...)`) | STDIO sobre subproceso | Servidores locales lanzados como proceso hijo |

Para el caso de un servidor MCP local lanzado como proceso (el patrón más común en prototipos), se usa `StdioServerParameters`:

```python
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

def server_params(server_script_path: str) -> StdioServerParameters:
    if server_script_path.endswith(".py"):
        command = "python"
    elif server_script_path.endswith(".js"):
        command = "node"
    else:
        raise ValueError("El script del servidor debe ser .py o .js")
    return StdioServerParameters(command=command, args=[server_script_path])
```

`StdioServerParameters` es solo configuración; `stdio_client()` la convierte en un transporte real, y `Client` abre ese transporte al entrar al bloque `async with`.

## Métodos Principales del `Client`

### Listar Herramientas Disponibles

```python
result = await client.list_tools()
for tool in result.tools:
    print(tool.name)
    print(tool.description)
    print(tool.input_schema)
```

`input_schema` es el JSON Schema derivado automáticamente de la función del servidor, es decir, lo que un LLM necesita para generar argumentos válidos al invocar la herramienta.

### Invocar una Herramienta

```python
result = await client.call_tool("search_books", {"query": "Dune"})
```

`call_tool()` devuelve un `CallToolResult` con tres componentes, cada uno con un consumidor distinto:

| Campo | Para quién | Descripción |
|---|---|---|
| `result.content` | El modelo (LLM) | Lista de bloques de contenido (`TextContent`, `ImageContent`, etc.) |
| `result.structured_content` | El código de la aplicación | El valor de retorno como JSON, sin necesidad de parsear texto |
| `result.is_error` | Manejo de errores | `True` si la herramienta falló |

**Punto importante:** si una herramienta lanza una excepción en el servidor, el cliente **no recibe una excepción**, sino un resultado normal con `is_error=True`. El mensaje de error queda disponible en `content`, de modo que el LLM puede leerlo e intentar de nuevo. Esto responde a una decisión de diseño deliberada de MCP: un error de herramienta forma parte de la conversación, no es un fallo del programa.

### Leer Recursos (Resources)

```python
listed = await client.list_resources()
templates = await client.list_resource_templates()
result = await client.read_resource("catalog://genres/poesia")
```

* `list_resources()` devuelve recursos con URI fija.
* `list_resource_templates()` devuelve recursos parametrizados (plantillas).
* `read_resource(uri)` funciona con ambos tipos.

### Obtener Prompts Predefinidos

```python
listed = await client.list_prompts()
result = await client.get_prompt("recommend", {"genre": "poesia"})
```

Devuelve una lista de mensajes (`role` + `content`) listos para pasarle directamente al LLM.

### Paginación

Todo método `list_*` acepta el parámetro `cursor=` y devuelve `next_cursor`. Se itera hasta que `next_cursor` sea `None`:

```python
tools = []
cursor = None
while True:
    page = await client.list_tools(cursor=cursor)
    tools.extend(page.tools)
    if page.next_cursor is None:
        break
    cursor = page.next_cursor
```

## Ejecución del Cliente

```bash
uv run client.py path/to/server.py
```

El flujo completo, una vez integrado con un LLM, sigue este patrón:

1. El cliente obtiene la lista de herramientas del servidor (`list_tools`).
2. La consulta del usuario se envía al LLM junto con las descripciones de las herramientas.
3. El LLM decide qué herramienta(s) usar.
4. El cliente ejecuta la(s) llamada(s) mediante `call_tool`.
5. Los resultados se devuelven al LLM.
6. El LLM genera una respuesta en lenguaje natural.
7. La respuesta se muestra al usuario.

## Buenas Prácticas

* Verificar `result.is_error` en lugar de esperar que una herramienta fallida lance una excepción.
* Dejar que el bloque `async with` controle todo el ciclo de vida de la conexión; no hay nada que cerrar manualmente.
* Guardar claves de API en variables de entorno (`.env`), nunca en el código fuente.
* Validar las respuestas del servidor antes de confiar en ellas, especialmente si el servidor no es propio.
* Ser cauteloso con los permisos otorgados a cada herramienta expuesta.

## Solución de Problemas Comunes

| Error | Causa probable |
|---|---|
| `FileNotFoundError` | Ruta incorrecta al script del servidor |
| `Connection refused` | El servidor no está corriendo o la ruta es incorrecta |
| `Tool execution failed` | Faltan variables de entorno requeridas por la herramienta |
| `Timeout error` | Considerar aumentar `read_timeout_seconds` en el `Client` |

---

## Referencias

> Model Context Protocol. (s.f.). *The Client - MCP Python SDK*. Model Context Protocol. https://py.sdk.modelcontextprotocol.io/client/

> Model Context Protocol. (s.f.). *Build an MCP client*. Model Context Protocol. https://modelcontextprotocol.io/docs/2026-07-28/develop/build-client
