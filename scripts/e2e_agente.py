"""Prueba de punta a punta: Agente A -> OAuth+DPoP -> MCP -> almacenamiento (solo lectura).

Uso (dentro de la red de Docker):
  MCP_BASE_URL=http://mcp-server:8000 MCP_USERNAME=... MCP_PASSWORD=... python scripts/e2e_agente.py
"""
import json
import os
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.oauth_client import DPoPA2AClient  # noqa: E402

URL = os.getenv("MCP_BASE_URL", "http://mcp-server:8000").rstrip("/") + "/mcp"
agente = DPoPA2AClient()
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
