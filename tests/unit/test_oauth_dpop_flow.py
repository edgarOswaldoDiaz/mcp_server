"""Prueba end-to-end del flujo OAuth + DPoP contra la app real (sin red)."""
import base64
import hashlib
import os
import time
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from starlette.testclient import TestClient

os.environ["MCP_AUTH_USERNAME"] = "agente_a"
os.environ["MCP_AUTH_PASSWORD"] = "pass-de-prueba"
os.environ["MCP_JWT_SECRET"] = "x" * 40
os.environ["MCP_REFRESH_SECRET"] = "y" * 40

from src.mcp.auth import oauth_handler as h  # noqa: E402
from src.mcp.server.main import app  # noqa: E402

BASE = "http://testserver"
INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                   "clientInfo": {"name": "t", "version": "1"}}}
MCP_HEADERS = {"Accept": "application/json, text/event-stream"}


def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


class Key:
    def __init__(self):
        self.k = ec.generate_private_key(ec.SECP256R1())
        n = self.k.public_key().public_numbers()
        self.jwk = {"kty": "EC", "crv": "P-256",
                    "x": b64u(n.x.to_bytes(32, "big")), "y": b64u(n.y.to_bytes(32, "big"))}

    def proof(self, method, url, token=None, jti=None):
        p = {"htm": method, "htu": url, "jti": jti or str(uuid.uuid4()), "iat": int(time.time())}
        if token:
            p["ath"] = b64u(hashlib.sha256(token.encode()).digest())
        return jwt.encode(p, self.k, algorithm="ES256",
                          headers={"typ": "dpop+jwt", "jwk": self.jwk})


@pytest.fixture()
def client():
    with TestClient(app, base_url=BASE) as c:
        yield c


def login(client, key):
    r = client.post("/oauth/token", json={"username": "agente_a", "password": "pass-de-prueba"},
                    headers={"DPoP": key.proof("POST", f"{BASE}/oauth/token")})
    assert r.status_code == 200, r.text
    return r.json()


def call_mcp(client, key, token, proof=None):
    return client.post("/mcp", json=INIT, headers={
        **MCP_HEADERS, "Authorization": f"DPoP {token}",
        "DPoP": proof or key.proof("POST", f"{BASE}/mcp", token)})


def test_sin_token_401(client):
    assert client.post("/mcp", json=INIT, headers=MCP_HEADERS).status_code == 401


def test_login_mal_password(client):
    k = Key()
    r = client.post("/oauth/token", json={"username": "agente_a", "password": "mal"},
                    headers={"DPoP": k.proof("POST", f"{BASE}/oauth/token")})
    assert r.status_code == 400


def test_bearer_simple_rechazado(client):
    k = Key(); t = login(client, k)["access_token"]
    r = client.post("/mcp", json=INIT, headers={**MCP_HEADERS, "Authorization": f"Bearer {t}"})
    assert r.status_code == 401


def test_flujo_feliz(client):
    k = Key(); d = login(client, k)
    assert d["token_type"] == "DPoP" and d["scope"] == "mcp:read"
    assert call_mcp(client, k, d["access_token"]).status_code == 200


def test_token_robado_con_otra_llave(client):
    k = Key(); t = login(client, k)["access_token"]
    ladron = Key()
    r = call_mcp(client, ladron, t)
    assert r.status_code == 401


def test_replay_de_la_misma_prueba(client):
    k = Key(); t = login(client, k)["access_token"]
    proof = k.proof("POST", f"{BASE}/mcp", t)
    assert call_mcp(client, k, t, proof).status_code == 200
    assert call_mcp(client, k, t, proof).status_code == 401


def test_refresh_mantiene_binding(client):
    k = Key(); d = login(client, k)
    r = client.post("/oauth/refresh", json={"refresh_token": d["refresh_token"]},
                    headers={"DPoP": k.proof("POST", f"{BASE}/oauth/refresh")})
    assert r.status_code == 200, r.text
    assert call_mcp(client, k, r.json()["access_token"]).status_code == 200


def test_refresh_con_otra_llave_falla(client):
    k = Key(); d = login(client, k)
    ladron = Key()
    r = client.post("/oauth/refresh", json={"refresh_token": d["refresh_token"]},
                    headers={"DPoP": ladron.proof("POST", f"{BASE}/oauth/refresh")})
    assert r.status_code == 401


def test_access_expirado_pide_refresh(client, monkeypatch):
    monkeypatch.setattr(h, "ACCESS_TTL", -5)
    k = Key(); t = login(client, k)["access_token"]
    r = call_mcp(client, k, t)
    assert r.status_code == 401 and "invalid_token" in r.headers["www-authenticate"]


def test_inactividad_cierra_sesion_y_bloquea_refresh(client):
    k = Key(); d = login(client, k)
    h.active_sessions["agente_a"] -= h.IDLE_TIMEOUT + 5      # simula 15+ min sin uso
    assert call_mcp(client, k, d["access_token"]).status_code == 401
    r = client.post("/oauth/refresh", json={"refresh_token": d["refresh_token"]},
                    headers={"DPoP": k.proof("POST", f"{BASE}/oauth/refresh")})
    assert r.status_code == 401
    d2 = login(client, k)                                     # login nuevo si funciona
    assert call_mcp(client, k, d2["access_token"]).status_code == 200


def test_docs_no_expuestas(client):
    for ruta in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(ruta).status_code in (401, 404)
