import os

from fastmcp.server.auth.providers.jwt import RSAKeyPair
from pydantic import SecretStr


PRIVATE_KEY_PATH = os.environ.get(
    "MCP_AUTH_PRIVATE_KEY_PATH",
    "/run/mcp-private/private_key.pem",
)

PUBLIC_KEY_PATH = os.environ.get(
    "MCP_AUTH_PUBLIC_KEY_PATH",
    "/run/mcp-public/public_key.pem",
)

TOKEN_OUTPUT_PATH = os.environ.get(
    "MCP_TOKEN_OUTPUT_PATH",
    "/run/mcp-token/access_token",
)

AUDIENCE = os.environ.get(
    "MCP_AUTH_AUDIENCE",
    "mcp-interoperability-server",
)

SUBJECT = os.environ.get(
    "MCP_TOKEN_SUBJECT",
    "a2a-agent",
)

SCOPES = os.environ.get(
    "MCP_TOKEN_SCOPES",
    "mcp:read mcp:tools",
).split()


def load_key_pair() -> RSAKeyPair:
    with open(PRIVATE_KEY_PATH, "r", encoding="utf-8") as file:
        private_key = file.read()

    with open(PUBLIC_KEY_PATH, "r", encoding="utf-8") as file:
        public_key = file.read()

    return RSAKeyPair(
        private_key=SecretStr(private_key),
        public_key=public_key,
    )


def main() -> None:
    os.makedirs(
        os.path.dirname(TOKEN_OUTPUT_PATH),
        mode=0o700,
        exist_ok=True,
    )

    key_pair = load_key_pair()

    token = key_pair.create_token(
        subject=SUBJECT,
        issuer="https://fastmcp.example.com",
        audience=AUDIENCE,
        scopes=SCOPES,
        expires_in_seconds=3600,
    )

    with open(TOKEN_OUTPUT_PATH, "w", encoding="utf-8") as file:
        file.write(token)

    os.chmod(TOKEN_OUTPUT_PATH, 0o600)

    print("A2A MCP access token generated successfully.")
    print(f"Subject: {SUBJECT}")
    print(f"Scopes: {' '.join(SCOPES)}")


if __name__ == "__main__":
    main()