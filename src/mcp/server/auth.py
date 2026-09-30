import os

from fastmcp.server.auth import JWTVerifier


def create_auth() -> JWTVerifier:
    """
    Creates the JWT authentication verifier for the MCP server.
    """

    public_key_path = os.environ.get(
        "MCP_AUTH_PUBLIC_KEY_PATH",
        os.path.expanduser("~/.mcp-keys/public_key.pem"),
    )

    audience = os.environ.get(
        "MCP_AUTH_AUDIENCE",
        "mcp-interoperability-server",
    )

    with open(public_key_path, "r", encoding="utf-8") as file:
        public_key = file.read()

    return JWTVerifier(
        public_key=public_key,
        audience=audience,
    )