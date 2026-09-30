import asyncio
import os

from fastmcp import Client


class MCPTestClient:
    """Modular class to run tests against the MCP server."""

    def __init__(self, server_url: str, token: str):
        self.server_url = server_url
        self.token = token

    async def _print_result(self, title: str, result) -> None:
        """Responsibility: Print a formatted tool result."""
        print(f"\n=== {title} ===")
        print("Data:")
        print(result.data)
        print("\nIs Error:")
        print(result.is_error)

    async def _list_tools(self, client: Client) -> None:
        """Responsibility: Fetch and display available tools."""
        tools = await client.list_tools()
        print("\n=== AVAILABLE TOOLS ===")
        for tool in tools:
            print(f"- {tool.name}")

    async def _list_resources(self, client: Client) -> None:
        """Responsibility: Fetch and display available resources."""
        resources = await client.list_resources()
        print("\n=== AVAILABLE RESOURCES ===")
        for resource in resources:
            print(f"- {resource.uri}")

    async def _list_prompts(self, client: Client) -> None:
        """Responsibility: Fetch and display available prompts."""
        prompts = await client.list_prompts()
        print("\n=== AVAILABLE PROMPTS ===")
        for prompt in prompts:
            print(f"- {prompt.name}")

    async def _run_tool_test(self, client: Client, tool_name: str, arguments: dict) -> None:
        """
        Responsibility: Call a tool and format its output.
        Open for extension: Supports any new tool without modifying this code.
        """
        print(f"\n=== TESTING: {tool_name.upper()} ===")
        try:
            result = await client.call_tool(tool_name, arguments)
            print("Result:")
            print(f"  {result.data}")
            if result.is_error:
                print(f"  [Warning] Is Error: {result.is_error}")
        except Exception as exc:
            print(f"  [!] Critical failure in tool: {exc}")

    async def _read_resource(self, client: Client, uri: str) -> None:
        """Responsibility: Read and display a specific resource."""
        print(f"\n=== READING RESOURCE: {uri} ===")
        try:
            resource = await client.read_resource(uri)
            print(resource)
        except Exception as exc:
            print(f"  [!] Failed to read resource: {exc}")

    async def _get_prompt(self, client: Client, prompt_name: str) -> None:
        """Responsibility: Fetch and display a specific prompt."""
        print(f"\n=== FETCHING PROMPT: {prompt_name} ===")
        try:
            prompt = await client.get_prompt(prompt_name)
            print(prompt)
        except Exception as exc:
            print(f"  [!] Failed to fetch prompt: {exc}")

    async def start_test_suite(self) -> None:
        """Responsibility: Orchestrate the connection and execution flow."""
        print(f"Connecting to: {self.server_url}...")

        async with Client(self.server_url, auth=self.token) as client:
            print("=== MCP CLIENT CONNECTED ===")

            # 1. Show what the server can do
            await self._list_tools(client)

            # 2. Run tool tests (easy to add more in the future)
            await self._run_tool_test(client, "echo", {"message": "Hello from MCP Client"})
            await self._run_tool_test(client, "add", {"a": 10, "b": 20})
            await self._run_tool_test(client, "get_system_status", {})

            # 3. List resources
            await self._list_resources(client)

            # 4. Read a specific resource
            await self._read_resource(client, "config://server")

            # 5. List prompts
            await self._list_prompts(client)

            # 6. Fetch a specific prompt
            await self._get_prompt(client, "system_diagnostic")


if __name__ == "__main__":
    # Dependency injection: Define the URL and token from outside
    token = os.environ["MCP_ACCESS_TOKEN"]
    tester = MCPTestClient("http://localhost:8000/mcp", token)
    asyncio.run(tester.start_test_suite())