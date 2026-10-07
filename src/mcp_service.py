from fastmcp import Client

class MCPService:
    def __init__(self, client: Client):
        self.client = client

    async def list_tools(self):
        return await self.client.list_tools()

    async def invoke_tool(self, tool_name: str, arguments: dict):
        return await self.client.call_tool(tool_name, arguments)

    async def fetch_resource(self, uri: str):
        return await self.client.read_resource(uri)
