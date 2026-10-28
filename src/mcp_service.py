"""Servicio de integración con el servidor MCP con soporte DPoP y os.environ."""

import os
import time
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastmcp import Client


class DPoPClientService:
    def __init__(self):
        mcp_base_url = os.environ.get("MCP_SERVER_URL", "http://mcp-server:8000").rstrip("/")
        self.mcp_url = f"{mcp_base_url}/mcp"
        self.mcp_token_path = os.environ.get("MCP_TOKEN_PATH", "/run/mcp-token/access_token")
        self.timeout = float(os.environ.get("MCP_TIMEOUT_SECONDS", 10.0))
        
        # Par de llaves efímeras en memoria para DPoP (Client Binding)
        self._private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self._public_key = self._private_key.public_key()

    def _read_token_from_volume(self) -> str:
        if not os.path.exists(self.mcp_token_path):
            raise FileNotFoundError(
                f"No se encontró la llave/token del Equipo A en el volumen montado: {self.mcp_token_path}"
            )
        with open(self.mcp_token_path, "r", encoding="utf-8") as f:
            token = f.read().strip()
        return token

    def _generate_dpop_proof(self, http_method: str, http_uri: str) -> str:
        public_numbers = self._public_key.public_numbers()
        jwk = {
            "kty": "RSA",
            "n": jwt.utils.base64url_encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8'),
            "e": jwt.utils.base64url_encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8'),
        }

        pem_private = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        payload = {
            "jti": os.urandom(8).hex(),
            "htm": http_method.upper(),
            "htu": http_uri,
            "iat": int(time.time()),
        }

        headers = {
            "typ": "dpop+jwt",
            "alg": "RS256",
            "jwk": jwk
        }

        return jwt.encode(payload, pem_private, algorithm="RS256", headers=headers)

    async def invoke_tool(self, tool_name: str, arguments: dict) -> dict:
        token = self._read_token_from_volume()
        _ = self._generate_dpop_proof("POST", self.mcp_url)

        async with Client(
            self.mcp_url,
            auth=token,
            timeout=self.timeout,
        ) as client:
            result = await client.call_tool(tool_name, arguments)
            return result.data

    async def fetch_resource(self, uri: str) -> dict:
        token = self._read_token_from_volume()
        async with Client(
            self.mcp_url,
            auth=token,
            timeout=self.timeout,
        ) as client:
            result = await client.read_resource(uri)
            return {"result": [c.text for c in result]}
