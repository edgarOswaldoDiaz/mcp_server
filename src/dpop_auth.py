"""Autenticador OAuth 2.0 + DPoP (RFC 9449) para el cliente MCP de FastMCP.

Se pasa como  Client(url, auth=DPoPAuth(...)). En CADA peticion firma una prueba DPoP nueva
(htm/htu/jti/iat/ath) y manda  Authorization: DPoP <token>.  Si el servidor responde 401,
renueva el access token con el refresh token (o vuelve a hacer login) y reintenta una vez.
La llave privada se genera en memoria y nunca sale del proceso.
"""
import asyncio
import base64
import hashlib
import time
import uuid

import httpx2
import jwt
from cryptography.hazmat.primitives.asymmetric import ec


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class DPoPAuth(httpx2.Auth):
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._key = ec.generate_private_key(ec.SECP256R1())
        n = self._key.public_key().public_numbers()
        self._jwk = {"kty": "EC", "crv": "P-256",
                     "x": _b64u(n.x.to_bytes(32, "big")), "y": _b64u(n.y.to_bytes(32, "big"))}
        self.access_token = None
        self.refresh_token = None
        self._lock = asyncio.Lock()

    # ---- pruebas DPoP -------------------------------------------------------------
    def _proof(self, method: str, url: str, access_token: str | None = None) -> str:
        claims = {"htm": method.upper(), "htu": url.split("?")[0].split("#")[0],
                  "jti": str(uuid.uuid4()), "iat": int(time.time())}
        if access_token:
            claims["ath"] = _b64u(hashlib.sha256(access_token.encode()).digest())
        return jwt.encode(claims, self._key, algorithm="ES256",
                          headers={"typ": "dpop+jwt", "jwk": self._jwk})

    def _sign(self, request: httpx2.Request) -> None:
        request.headers["Authorization"] = f"DPoP {self.access_token}"
        request.headers["DPoP"] = self._proof(request.method, str(request.url), self.access_token)

    # ---- peticiones al servidor OAuth ----------------------------------------------
    def _login_request(self) -> httpx2.Request:
        url = f"{self.base_url}/oauth/token"
        return httpx2.Request("POST", url, json={"username": self.username, "password": self.password},
                              headers={"DPoP": self._proof("POST", url)})

    def _refresh_request(self) -> httpx2.Request:
        url = f"{self.base_url}/oauth/refresh"
        return httpx2.Request("POST", url, json={"refresh_token": self.refresh_token},
                              headers={"DPoP": self._proof("POST", url)})

    def _store(self, response: httpx2.Response) -> bool:
        if response.status_code != 200:
            return False
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        return True

    # ---- flujo httpx -----------------------------------------------------------------
    async def async_auth_flow(self, request):
        async with self._lock:
            if not self.access_token:
                resp = yield self._login_request()
                await resp.aread()
                if not self._store(resp):
                    raise RuntimeError(f"Login OAuth fallido ({resp.status_code}): {resp.text[:200]}")
        self._sign(request)
        response = yield request
        if response.status_code != 401:
            return
        await response.aread()
        async with self._lock:               # token vencido/inactivo: renovar y reintentar UNA vez
            renovado = False
            if self.refresh_token:
                resp = yield self._refresh_request()
                await resp.aread()
                renovado = self._store(resp)
            if not renovado:
                resp = yield self._login_request()
                await resp.aread()
                if not self._store(resp):
                    raise RuntimeError(f"No se pudo renovar la sesion ({resp.status_code})")
        self._sign(request)
        yield request
