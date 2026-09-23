import os

import pytest


SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "http://localhost:8000/mcp",
)


@pytest.fixture(scope="session")
def mcp_server():
    return SERVER_URL



