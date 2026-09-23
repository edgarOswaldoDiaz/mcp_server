from fastmcp import Client
import pytest
import json
from fastmcp.exceptions import ToolError


async def test_list_tools(mcp_server):

    async with Client(mcp_server) as client:

        tools = await client.list_tools()

        tool_names = {
            tool.name
            for tool in tools
        }

        assert "echo" in tool_names
        assert "add" in tool_names
        assert "get_system_status" in tool_names


async def test_echo(mcp_server):

    async with Client(mcp_server) as client:

        result = await client.call_tool(
            "echo",
            {
                "message": "integration test"
            }
        )

        assert result.is_error is False

        assert result.data == {
            "message": "integration test"
        }


async def test_add(mcp_server):

    async with Client(mcp_server) as client:

        result = await client.call_tool(
            "add",
            {
                "a": 10,
                "b": 20
            }
        )

        assert result.is_error is False

        assert result.data == {
            "result": 30
        }


async def test_system_status(mcp_server):

    async with Client(mcp_server) as client:

        result = await client.call_tool(
            "get_system_status"
        )

        assert result.is_error is False
        assert result.data["status"] == "healthy"

async def test_list_resources(mcp_server):

    async with Client(mcp_server) as client:

        resources = await client.list_resources()

        resource_uris = {
            str(resource.uri)
            for resource in resources
        }

        assert "config://server" in resource_uris


async def test_read_server_config(mcp_server):

    async with Client(mcp_server) as client:

        result = await client.read_resource(
            "config://server"
        )

        assert len(result) == 1

        config = json.loads(result[0].text)

        assert config["name"] == "MCP Interoperability Server"
        assert config["version"] == "0.1.0"
        assert config["environment"] == "development"


async def test_list_prompts(mcp_server):

    async with Client(mcp_server) as client:

        prompts = await client.list_prompts()

        prompt_names = {
            prompt.name
            for prompt in prompts
        }

        assert "system_diagnostic" in prompt_names


async def test_get_system_diagnostic_prompt(mcp_server):

    async with Client(mcp_server) as client:

        result = await client.get_prompt(
            "system_diagnostic"
        )

        assert len(result.messages) > 0


async def test_invalid_tool_arguments(mcp_server):

    async with Client(mcp_server) as client:

        with pytest.raises(ToolError):

            await client.call_tool(
                "add",
                {
                    "a": 10,
                    "b": "invalid"
                }
            )


async def test_unknown_tool(mcp_server):

    async with Client(mcp_server) as client:

        with pytest.raises(ToolError):

            await client.call_tool(
                "does_not_exist"
            )