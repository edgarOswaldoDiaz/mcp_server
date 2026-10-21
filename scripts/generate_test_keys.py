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



    private_key_path = os.path.join(
        PRIVATE_KEYS_DIR,
        "private_key.pem",
    )

    public_key_path = os.path.join(
        PUBLIC_KEYS_DIR,
        "public_key.pem",
    )

    # Si ambas llaves existen, las conservamos.
    private_exists = os.path.isfile(private_key_path)
    public_exists = os.path.isfile(public_key_path)

    if private_exists and public_exists:
        print("RSA keys already exist. Keeping existing keys.")
        return

    if private_exists != public_exists:
        raise RuntimeError(
            "Incomplete RSA key pair. Both keys must exist or neither. "
            "Inspect the mounted volumes before regenerating keys."
        )

    key_pair = RSAKeyPair.generate()

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