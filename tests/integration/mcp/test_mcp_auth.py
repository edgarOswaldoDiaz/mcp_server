import os

import pytest
from fastmcp import Client
from fastmcp.server.auth.providers.jwt import RSAKeyPair
from pydantic import SecretStr
from mcp.shared.exceptions import MCPError


MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "http://localhost:8000/mcp",
)

PRIVATE_KEY_PATH = os.environ.get(
    "MCP_AUTH_PRIVATE_KEY_PATH",
    os.path.expanduser("~/.mcp-keys/private_key.pem"),
)

PUBLIC_KEY_PATH = os.environ.get(
    "MCP_AUTH_PUBLIC_KEY_PATH",
    os.path.expanduser("~/.mcp-keys/public_key.pem"),
)

AUDIENCE = "mcp-interoperability-server"

# ---------------------------------------------
#       Load Private and Public Keys
# ---------------------------------------------

def load_key_pair() -> RSAKeyPair:
    """Load the RSA key pair used by the development MCP server."""

    with open(PRIVATE_KEY_PATH, "r", encoding="utf-8") as file:
        private_key = file.read()

    with open(PUBLIC_KEY_PATH, "r", encoding="utf-8") as file:
        public_key = file.read()

    return RSAKeyPair(
        private_key=SecretStr(private_key),
        public_key=public_key,
    )

# ---------------------------------------------
#               Create Token
# ---------------------------------------------
def create_token(scopes: list[str]) -> str:
    """Create a JWT for integration testing."""

    key_pair = load_key_pair()

    return key_pair.create_token(
        subject="integration-test-user",
        issuer="https://fastmcp.example.com",
        audience=AUDIENCE,
        scopes=scopes,
        expires_in_seconds=3600,
    )

# ---------------------------------------------
#           Create Custom Token
# ---------------------------------------------
def create_custom_token(
    *,
    audience: str | None = AUDIENCE,
    expires_in_seconds: int = 3600,
    scopes: list[str] | None = None,
) -> str:
    """Create a JWT with customizable claims for authentication tests."""

    key_pair = load_key_pair()

    return key_pair.create_token(
        subject="integration-test-user",
        issuer="https://fastmcp.example.com",
        audience=audience,
        scopes=scopes,
        expires_in_seconds=expires_in_seconds,
    )

# ---------------------------------------------
#               List Authorized Tools
# ---------------------------------------------
async def get_tool_names(client: Client) -> list[str]:
    """Return the names of tools visible to the authenticated client."""

    tools = await client.list_tools()

    return [tool.name for tool in tools]

# ------------------------------- Authentication ------------------------- #
@pytest.mark.asyncio
async def test_missing_token_is_rejected():

    with pytest.raises(MCPError) as exc_info:

        async with Client(
            MCP_SERVER_URL,
        ):
            pass

    assert exc_info.value.code == -32603
    assert exc_info.value.message == "Server returned an error response"


@pytest.mark.asyncio
async def test_invalid_token_is_rejected():

    with pytest.raises(MCPError) as exc_info:

        async with Client(
            MCP_SERVER_URL,
            auth="token-falso",
        ):
            pass

    assert exc_info.value.code == -32603
    assert exc_info.value.message == "Server returned an error response"


@pytest.mark.asyncio
async def test_wrong_audience_is_rejected():

    token = create_custom_token(
        audience="wrong-audience",
    )

    with pytest.raises(MCPError) as exc_info:

        async with Client(
            MCP_SERVER_URL,
            auth=token,
        ):
            pass

    assert exc_info.value.code == -32603
    assert exc_info.value.message == "Server returned an error response"


@pytest.mark.asyncio
async def test_expired_token_is_rejected():

    token = create_custom_token(
        expires_in_seconds=-1,
    )

    with pytest.raises(MCPError) as exc_info:

        async with Client(
            MCP_SERVER_URL,
            auth=token,
        ):
            pass

    assert exc_info.value.code == -32603
    assert exc_info.value.message == "Server returned an error response"


# ------------------------------- Authorization ------------------------- #      
@pytest.mark.asyncio
async def test_read_scope_can_access_read_tools():

    token = create_token(["mcp:read"])

    async with Client(
        MCP_SERVER_URL,
        auth=token,
    ) as client:

        tool_names = await get_tool_names(client)

        assert "get_system_status" in tool_names
        assert "echo" in tool_names
        assert "add" not in tool_names

        result = await client.call_tool(
            "echo",
            {"message": "integration test"},
        )

        assert result.data == {
            "message": "integration test"
        }


@pytest.mark.asyncio
async def test_tools_scope_can_access_add():

    token = create_token(["mcp:tools"])

    async with Client(
        MCP_SERVER_URL,
        auth=token,
    ) as client:

        tool_names = await get_tool_names(client)

        assert "add" in tool_names
        assert "get_system_status" not in tool_names
        assert "echo" not in tool_names

        result = await client.call_tool(
            "add",
            {
                "a": 10,
                "b": 20,
            },
        )

        assert result.data == {
            "result": 30
        }


@pytest.mark.asyncio
async def test_both_scopes_can_access_all_tools():

    token = create_token(
        [
            "mcp:read",
            "mcp:tools",
        ]
    )

    async with Client(
        MCP_SERVER_URL,
        auth=token,
    ) as client:

        tool_names = await get_tool_names(client)

        assert "get_system_status" in tool_names
        assert "echo" in tool_names
        assert "add" in tool_names

        echo_result = await client.call_tool(
            "echo",
            {"message": "integration test"},
        )

        assert echo_result.data == {
            "message": "integration test"
        }

        add_result = await client.call_tool(
            "add",
            {
                "a": 10,
                "b": 20,
            },
        )

        assert add_result.data == {
            "result": 30
        }