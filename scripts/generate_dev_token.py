import os
import sys

from pydantic import SecretStr

from fastmcp.server.auth.providers.jwt import RSAKeyPair


PRIVATE_KEY_PATH = os.path.expanduser(
    "~/.mcp-keys/private_key.pem"
)

PUBLIC_KEY_PATH = os.path.expanduser(
    "~/.mcp-keys/public_key.pem"
)

AUDIENCE = "mcp-interoperability-server"


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

    scopes = sys.argv[1:]

    if not scopes:
        print("Usage: python scripts/generate_dev_token.py <scope>...")
        return

    key_pair = load_key_pair()

    token = key_pair.create_token(
        subject="dev-user",
        issuer="https://fastmcp.example.com",
        audience=AUDIENCE,
        scopes=scopes,
        expires_in_seconds=3600,
    )

    print(token)


if __name__ == "__main__":
    main()