import os
import time
import uuid
import base64
import hashlib
import requests
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from dotenv import load_dotenv

load_dotenv()

class DPoPA2AClient:
    def __init__(self, base_url=None, username=None, password=None):
        self.base_url = (base_url or os.getenv("MCP_BASE_URL", "http://localhost:8000")).rstrip('/')
        self.auth_url = f"{self.base_url}/oauth/token"
        self.refresh_url = f"{self.base_url}/oauth/refresh"
        
        self.username = username or os.getenv("MCP_USERNAME", "admin_mcp")
        self.password = password or os.getenv("MCP_PASSWORD", "seguridad123")

        # Generar par de claves asimétricas ECDSA P-256 (RFC 9449)
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

        self.access_token = None
        self.refresh_token = None
        self.server_nonce = None

    def _get_public_jwk(self) -> dict:
        """Exporta la clave pública al formato JWK requerido por DPoP."""
        numbers = self.public_key.public_numbers()
        
        def b64_u(num_bytes: bytes) -> str:
            return base64.urlsafe_b64encode(num_bytes).decode('utf-8').rstrip('=')

        x_bytes = numbers.x.to_bytes(32, byteorder='big')
        y_bytes = numbers.y.to_bytes(32, byteorder='big')

        return {
            "kty": "EC",
            "crv": "P-256",
            "x": b64_u(x_bytes),
            "y": b64_u(y_bytes)
        }

    def _create_dpop_proof(self, method: str, url: str, access_token: str = None) -> str:
        """Crea y firma el JWT de prueba DPoP con la clave privada P-256."""
        payload = {
            "htm": method.upper(),
            "htu": url,
            "jti": str(uuid.uuid4()),
            "iat": int(time.time())
        }

        if self.server_nonce:
            payload["nonce"] = self.server_nonce

        if access_token:
            ath_hash = hashlib.sha256(access_token.encode('utf-8')).digest()
            payload["ath"] = base64.urlsafe_b64encode(ath_hash).decode('utf-8').rstrip('=')

        headers = {
            "typ": "dpop+jwt",
            "alg": "ES256",
            "jwk": self._get_public_jwk()
        }

        return jwt.encode(payload, self.private_key, algorithm="ES256", headers=headers)

    def request_access_token(self):
        """Solicita el token de acceso con JSON (username/password) y cabecera DPoP."""
        dpop_proof = self._create_dpop_proof("POST", self.auth_url)

        headers = {
            "DPoP": dpop_proof,
            "Content-Type": "application/json"
        }

        data = {
            "username": self.username,
            "password": self.password
        }

        response = requests.post(self.auth_url, json=data, headers=headers)

        if "DPoP-Nonce" in response.headers:
            self.server_nonce = response.headers["DPoP-Nonce"]

        response.raise_for_status()
        res_data = response.json()

        self.access_token = res_data.get("access_token")
        self.refresh_token = res_data.get("refresh_token")
        return self.access_token

    def refresh_access_token(self):
        """Renueva el token expirado usando /oauth/refresh."""
        if not self.refresh_token:
            return self.request_access_token()

        dpop_proof = self._create_dpop_proof("POST", self.refresh_url)
        headers = {
            "DPoP": dpop_proof,
            "Content-Type": "application/json"
        }
        data = {
            "refresh_token": self.refresh_token
        }

        response = requests.post(self.refresh_url, json=data, headers=headers)

        if "DPoP-Nonce" in response.headers:
            self.server_nonce = response.headers["DPoP-Nonce"]

        if response.status_code == 200:
            res_data = response.json()
            self.access_token = res_data.get("access_token")
            if "refresh_token" in res_data:
                self.refresh_token = res_data.get("refresh_token")
            return self.access_token
        else:
            return self.request_access_token()

    def send_authenticated_request(self, method: str, url: str, json_data: dict = None):
        """Envía peticiones al MCP con 'Authorization: DPoP <token>' y manejo de reintentos."""
        if not self.access_token:
            self.request_access_token()

        dpop_proof = self._create_dpop_proof(method, url, self.access_token)
        headers = {
            "DPoP": dpop_proof,
            "Authorization": f"DPoP {self.access_token}"
        }

        response = requests.request(method, url, json=json_data, headers=headers)

        if "DPoP-Nonce" in response.headers:
            self.server_nonce = response.headers["DPoP-Nonce"]

        if response.status_code in (400, 401):
            www_auth = response.headers.get("WWW-Authenticate", "")
            if "use_dpop_nonce" in www_auth or "invalid_token" in www_auth:
                self.refresh_access_token()
                dpop_proof = self._create_dpop_proof(method, url, self.access_token)
                headers["DPoP"] = dpop_proof
                headers["Authorization"] = f"DPoP {self.access_token}"
                response = requests.request(method, url, json=json_data, headers=headers)

        return response