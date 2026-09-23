import asyncio
from fastmcp import Client

class ClientePruebasMCP:
    """Clase modular para ejecutar pruebas contra el servidor MCP del INEGI."""

    def __init__(self, url_servidor: str):
        self.url_servidor = url_servidor

    async def _listar_herramientas(self, client: Client) -> None:
        """Responsabilidad: Únicamente obtener y mostrar las herramientas disponibles."""
        tools = await client.list_tools()
        print("\n=== HERRAMIENTAS DISPONIBLES ===")
        for tool in tools:
            print(f"- {tool.name}")

    async def _ejecutar_prueba(self, client: Client, nombre_herramienta: str, argumentos: dict) -> None:
        """
        Responsabilidad: Llamar a una herramienta y formatear su salida.
        Abierto a extensión: Soporta cualquier herramienta nueva sin modificar este código.
        """
        print(f"\n=== PROBANDO: {nombre_herramienta.upper()} ===")
        try:
            result = await client.call_tool(nombre_herramienta, argumentos)
            print("Resultado:")
            print(f"  {result.data}")
            if result.is_error:
                print(f"  [Advertencia] Is Error: {result.is_error}")
        except Exception as exc:
            print(f"  [!] Fallo crítico en la herramienta: {exc}")

    async def iniciar_bateria_pruebas(self) -> None:
        """Responsabilidad: Orquestar la conexión y el flujo de ejecución."""
        print(f"Conectando a: {self.url_servidor}...")
        
        async with Client(self.url_servidor) as client:
            print("=== CLIENTE MCP CONECTADO ===")
            
            # 1. Mostrar qué sabe hacer el servidor
            await self._listar_herramientas(client)

            # 2. Ejecutar las pruebas (muy fácil agregar más en el futuro)
            await self._ejecutar_prueba(client, "echo", {"mensaje": "Hola desde la nueva arquitectura"})
            await self._ejecutar_prueba(client, "sumar", {"a": 10, "b": 20})

if __name__ == "__main__":
    # Inyección de dependencia: Definimos la ruta desde afuera
    tester = ClientePruebasMCP("http://localhost:8000/sse")
    asyncio.run(tester.iniciar_bateria_pruebas())