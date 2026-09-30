import os

from fastmcp.server.auth.providers.jwt import RSAKeyPair


PUBLIC_KEYS_DIR = os.environ.get(
    "MCP_PUBLIC_KEYS_DIR",
    "/run/mcp-public",
)

PRIVATE_KEYS_DIR = os.environ.get(
    "MCP_PRIVATE_KEYS_DIR",
    "/run/mcp-private",
)


def main() -> None:
    os.makedirs(PUBLIC_KEYS_DIR, mode=0o700, exist_ok=True)
    os.makedirs(PRIVATE_KEYS_DIR, mode=0o700, exist_ok=True)

    key_pair = RSAKeyPair.generate()

    private_key_path = os.path.join(
        PRIVATE_KEYS_DIR,
        "private_key.pem",
    )

    public_key_path = os.path.join(
        PUBLIC_KEYS_DIR,
        "public_key.pem",
    )

    with open(
        private_key_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            key_pair.private_key.get_secret_value()
        )

    with open(
        public_key_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(key_pair.public_key)

    os.chmod(private_key_path, 0o600)
    os.chmod(public_key_path, 0o644)

    print("Test RSA keys generated successfully.")


if __name__ == "__main__":
    main()