import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.config import settings

class MCPService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True
    )
    async def invoke_tool(self, tool_name: str, arguments: dict) -> dict:
        response = await self.client.post(
            f"{settings.mcp_server_url}/tools/call",
            json={"name": tool_name, "arguments": arguments},
            timeout=settings.mcp_timeout_seconds
        )
        response.raise_for_status()
        return response.json()

    async def fetch_resource(self, uri: str) -> dict:
        response = await self.client.get(
            f"{settings.mcp_server_url}/resources/read",
            params={"uri": uri},
            timeout=settings.mcp_timeout_seconds
        )
        response.raise_for_status()
        return response.json()