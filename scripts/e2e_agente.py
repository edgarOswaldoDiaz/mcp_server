"""Prueba de punta a punta del lado del MCP: cliente de prueba -> OAuth+DPoP -> MCP -> almacenamiento (solo lectura).

Uso (dentro de la red de Docker):
  MCP_BASE_URL=http://mcp-server:8000 MCP_USERNAME=... MCP_PASSWORD=... python scripts/e2e_agente.py
"""
import base64
import hashlib
import json
import os
import sys
import time
import uuid

import jwt
import requests
from cryptography.hazmat.primitives.asymmetric import ec


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


class ClienteDPoP:
    """Cliente de PRUEBA, autocontenido: no depende del codigo de ningun otro equipo.

    Solo habla el protocolo publico del MCP (OAuth 2.0 + DPoP, RFC 9449).
    """

    def __init__(self):
        base = os.getenv("MCP_BASE_URL", "http://mcp-server:8000").rstrip("/")
        self.auth_url, self.refresh_url = f"{base}/oauth/token", f"{base}/oauth/refresh"
        self.username = os.getenv("MCP_USERNAME", "")
        self.password = os.getenv("MCP_PASSWORD", "")
        self._key = ec.generate_private_key(ec.SECP256R1())
        n = self._key.public_key().public_numbers()
        self._jwk = {"kty": "EC", "crv": "P-256",
                     "x": _b64u(n.x.to_bytes(32, "big")), "y": _b64u(n.y.to_bytes(32, "big"))}
        self.access_token = None
        self.refresh_token = None

    def _create_dpop_proof(self, method, url, access_token=None):
        claims = {"htm": method.upper(), "htu": url, "jti": str(uuid.uuid4()), "iat": int(time.time())}
        if access_token:
            claims["ath"] = _b64u(hashlib.sha256(access_token.encode()).digest())
        return jwt.encode(claims, self._key, algorithm="ES256",
                          headers={"typ": "dpop+jwt", "jwk": self._jwk})

    def _post(self, url, body):
        return requests.post(url, json=body, headers={"DPoP": self._create_dpop_proof("POST", url)}, timeout=30)

    def request_access_token(self):
        r = self._post(self.auth_url, {"username": self.username, "password": self.password})
        r.raise_for_status()
        d = r.json()
        self.access_token, self.refresh_token = d["access_token"], d["refresh_token"]

    def refresh_access_token(self):
        if self.refresh_token:
            r = self._post(self.refresh_url, {"refresh_token": self.refresh_token})
            if r.status_code == 200:
                self.access_token = r.json()["access_token"]
                return
        self.request_access_token()


URL = os.getenv("MCP_BASE_URL", "http://mcp-server:8000").rstrip("/") + "/mcp"
agente = ClienteDPoP()
sesion = {"id": None}
_n = {"i": 0}


def rpc(method, params=None, notify=False):
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        body["params"] = params
    if not notify:
        _n["i"] += 1
        body["id"] = _n["i"]

    def enviar():
        h = {"DPoP": agente._create_dpop_proof("POST", URL, agente.access_token),
             "Authorization": f"DPoP {agente.access_token}",
             "Accept": "application/json, text/event-stream"}
        if sesion["id"]:
            h["Mcp-Session-Id"] = sesion["id"]
        return requests.post(URL, json=body, headers=h, timeout=60)

    r = enviar()
    if r.status_code == 401:                  # token vencido/invalido -> renovar y reintentar
        print("   (401: renovando token con el refresh token...)")
        agente.refresh_access_token()
        r = enviar()
    sesion["id"] = r.headers.get("mcp-session-id", sesion["id"])
    if notify:
        return r.status_code, None
    for linea in r.text.splitlines():
        if linea.startswith("data:"):
            return r.status_code, json.loads(linea[5:])
    return r.status_code, (r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text)


def llamar(tool, **args):
    return rpc("tools/call", {"name": tool, "arguments": args})


def corto(x, n=160):
    s = json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x
    return s[:n] + ("..." if len(s) > n else "")


ok = True
print("1) Login OAuth + DPoP")
agente.request_access_token()
print("   token obtenido, tipo DPoP: OK")

print("2) Inicializar sesion MCP")
st, resp = rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                              "clientInfo": {"name": "agente-a", "version": "1"}})
print("  ", st, "OK" if st == 200 else "FALLO"); ok &= st == 200
rpc("notifications/initialized", notify=True)

print("3) Herramientas disponibles")
st, resp = rpc("tools/list", {})
nombres = [t["name"] for t in resp["result"]["tools"]]
print("  ", nombres)
escritura = [n for n in nombres if any(p in n.lower() for p in ("write", "put", "delete", "upload", "remove"))]
print("   herramientas de escritura:", escritura or "ninguna (solo lectura): OK"); ok &= not escritura

print("4) Leer JSON confidencial")
st, resp = llamar("read_minio_json", object_key="metadatos/ingresos_sinteticos.json")
print("  ", st, corto(resp.get("result", resp))); ok &= st == 200 and "error" not in resp and not resp["result"].get("isError")

print("5) Leer Parquet confidencial")
st, resp = llamar("read_minio_parquet", object_key="ingresos/ingresos_sinteticos.parquet")
print("  ", st, corto(resp.get("result", resp))); ok &= st == 200 and not resp["result"].get("isError")

print("6) Renovacion: token invalido a proposito")
agente.access_token = "token-invalido"
st, resp = rpc("tools/list", {})
print("  ", st, "renovado y funcionando: OK" if st == 200 else "FALLO"); ok &= st == 200

print("7) Objeto inexistente debe fallar limpio")
st, resp = llamar("read_minio_json", object_key="no/existe.json")
print("  ", corto(resp.get("result", resp)))

print("\nRESULTADO:", "TODO OK" if ok else "HAY FALLOS")
sys.exit(0 if ok else 1)
