import os

import pytest
from fastmcp.server.auth.providers.jwt import RSAKeyPair
from pydantic import SecretStr


SERVER_URL = os.getenv(
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

AUDIENCE = os.environ.get(
    "MCP_AUTH_AUDIENCE",
    "mcp-interoperability-server",
)


@pytest.fixture(scope="session")
def mcp_server():
    return SERVER_URL


@pytest.fixture(scope="session")
def mcp_key_pair():
    with open(PRIVATE_KEY_PATH, "r", encoding="utf-8") as file:
        private_key = file.read()

    with open(PUBLIC_KEY_PATH, "r", encoding="utf-8") as file:
        public_key = file.read()

    return RSAKeyPair(
        private_key=SecretStr(private_key),
        public_key=public_key,
    )


@pytest.fixture(scope="session")
def mcp_access_token(mcp_key_pair):
    return mcp_key_pair.create_token(
        subject="integration-test-user",
        issuer="https://fastmcp.example.com",
        audience=AUDIENCE,
        scopes=[
            "mcp:read",
            "mcp:tools",
        ],
        expires_in_seconds=3600,
    )



