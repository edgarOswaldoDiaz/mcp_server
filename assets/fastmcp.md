# 2.2 FastMCP como Capa de Abstracción

## ¿Qué es FastMCP?

FastMCP surge como una capa de abstracción sobre MCP: un framework que se encarga del trabajo repetitivo para que el desarrollador pueda concentrarse únicamente en la lógica de la aplicación. FastMCP traduce funciones y objetos de Python en componentes MCP completamente funcionales (herramientas, recursos, prompts), aplicando buenas prácticas de forma automática y transparente.

 ## Origen y Adopción

FastMCP nació ligado al propio ecosistema MCP: su primera versión (FastMCP 1.0) terminó integrándose al SDK oficial de Python de MCP en 2024. A partir de ahí, el proyecto continuó su desarrollo de forma independiente y hoy es mantenido activamente como el framework de facto para trabajar con el protocolo.

Su nivel de adopción es significativo: se estima que el proyecto se descarga alrededor de un millón de veces al día, y que alguna versión de FastMCP impulsa aproximadamente el 70% de los servidores MCP existentes, considerando todos los lenguajes de programación.

## Los Tres Pilares de FastMCP
 
FastMCP organiza sus capacidades en tres grandes componentes, cada uno correspondiente a un rol distinto dentro del ecosistema MCP:
 
### 1. Servers (Servidores)
 
Permiten envolver funciones de Python y convertirlas automáticamente en herramientas, recursos y prompts compatibles con MCP. Al declarar una función y decorarla (por ejemplo, con `@mcp.tool`), FastMCP genera de manera automática el esquema de parámetros, la validación de tipos y la documentación asociada, sin que el desarrollador tenga que escribir ese código de forma manual.
 
Un ejemplo mínimo de servidor luce así:
 
```python
from fastmcp import FastMCP
 
mcp = FastMCP("Demo")
 
@mcp.tool
def add(a: int, b: int) -> int:
    """Suma dos números"""
    return a + b
 
if __name__ == "__main__":
    mcp.run()
```
 
Con apenas estas líneas, la función `add` queda expuesta como una herramienta MCP completamente funcional, lista para ser descubierta e invocada por cualquier cliente compatible.
 
### 2. Apps (Aplicaciones)
 
Este pilar permite dotar a las herramientas de interfaces interactivas que se renderizan directamente dentro de la conversación con el modelo. Es decir, una herramienta no solo puede devolver datos, sino también una experiencia visual e interactiva integrada al flujo conversacional.
 
### 3. Clients (Clientes)
 
FastMCP también facilita la construcción de clientes capaces de conectarse a cualquier servidor MCP, ya sea local o remoto, y sin importar si el servidor fue construido con FastMCP o con otra implementación del protocolo. El cliente maneja de forma transparente la negociación de transporte, la autenticación y el ciclo de vida de la conexión.
 
Un ejemplo de cliente que consulta un servidor remoto:
 
```python
import asyncio
from fastmcp import Client
 
async def main():
    async with Client("https://ejemplo.com/mcp") as client:
        result = await client.call_tool(
            name="nombre_de_la_herramienta",
            arguments={"parametro": "valor"}
        )
    print(result)
 
asyncio.run(main())
```

## FastMCP como Estándar de Facto
 
Gracias a que resuelve automáticamente los aspectos más tediosos de implementar MCP (esquemas, validación, transporte, autenticación y ciclo de vida del protocolo), FastMCP funciona como una verdadera capa de abstracción: permite que cualquier persona con conocimientos de Python pueda construir servidores, clientes o aplicaciones MCP de nivel productivo sin necesidad de dominar los detalles internos de la especificación del protocolo.
 
Esta filosofía de "las buenas prácticas ya vienen incorporadas" es lo que ha llevado a que el proyecto se convierta en el framework estándar dentro del ecosistema, y explica por qué buena parte de los servidores MCP disponibles actualmente están construidos sobre esta base, independientemente del lenguaje utilizado.

## Referencias
 
> FastMCP. (s.f.) *Welcome to FastMCP*. Documentación oficial. gofastmcp.com. https://gofastmcp.com/getting-started/welcome
