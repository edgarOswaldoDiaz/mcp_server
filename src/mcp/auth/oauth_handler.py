"""OAuth 2.0 + DPoP (RFC 9449) para el MCP Server.

Todo lo sensible viene de variables de entorno (nada de secretos en el codigo):

  MCP_JWT_SECRET            firma de access tokens        (obligatoria en produccion)
  MCP_REFRESH_SECRET        firma de refresh tokens       (obligatoria en produccion)
  MCP_AUTH_USERNAME         usuario del agente            (obligatoria)
  MCP_AUTH_PASSWORD         contrasena del agente         (obligatoria)
  MCP_IDLE_TIMEOUT_SECONDS  inactividad maxima, def. 900  (15 min)
  MCP_ACCESS_TTL_SECONDS    vida del access token, def. 600 (10 min)
  MCP_REFRESH_TTL_SECONDS   vida del refresh token, def. 604800 (7 dias)
  MCP_PUBLIC_BASE_URL       URL publica para validar 'htu' detras de proxy (opcional)
  MCP_REQUIRED_SCOPE        scope exigido en /mcp, def. mcp:read
"""
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import threading
import time

import jwt
from fastapi import HTTPException, Request

log = logging.getLogger("mcp.auth")

ALGORITHM = "HS256"          # firma de NUESTROS tokens (simetrica, solo la conoce el servidor)
DPOP_ALGS = ["ES256"]        # firma de la prueba DPoP del cliente (asimetrica)
DPOP_IAT_WINDOW = 60         # segundos de tolerancia del reloj
GRANTED_SCOPE = "mcp:read"   # el agente SOLO recibe lectura


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def _secret(name: str) -> str:
    value = os.environ.get(name)
    if value:
        return value
    log.warning("%s no esta definida: se usa un secreto aleatorio (los tokens "
                "no sobreviven a un reinicio). Defínela en .env.", name)
    return secrets.token_urlsafe(48)


SECRET_KEY = _secret("MCP_JWT_SECRET")
REFRESH_SECRET_KEY = _secret("MCP_REFRESH_SECRET")
IDLE_TIMEOUT = _env_int("MCP_IDLE_TIMEOUT_SECONDS", 900)
ACCESS_TTL = _env_int("MCP_ACCESS_TTL_SECONDS", 600)
REFRESH_TTL = _env_int("MCP_REFRESH_TTL_SECONDS", 604800)
REQUIRED_SCOPE = os.environ.get("MCP_REQUIRED_SCOPE", GRANTED_SCOPE)

# usuario -> timestamp (monotonic-ish, time.time) de la ultima actividad valida
active_sessions: dict[str, float] = {}
# jti -> expiracion; evita reutilizar una prueba DPoP capturada (replay)
_seen_jti: dict[str, float] = {}
_lock = threading.Lock()


# --------------------------------------------------------------------------- utilidades
def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def compute_jwk_thumbprint(jwk: dict) -> str:
    """JWK Thumbprint (RFC 7638)."""
    kty = jwk.get("kty")
    try:
        if kty == "EC":
            canonical = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
        elif kty == "RSA":
            canonical = {"e": jwk["e"], "kty": "RSA", "n": jwk["n"]}
        else:
            raise KeyError(kty)
    except KeyError:
        raise HTTPException(status_code=400, detail="JWK no soportado para DPoP")
    raw = json.dumps(canonical, separators=(",", ":"), sort_keys=True).encode()
    return _b64u(hashlib.sha256(raw).digest())


def _auth_error(status: int, error: str, description: str) -> HTTPException:
    """Error con WWW-Authenticate (RFC 6750/9449); el cliente de Isa busca 'invalid_token'."""
    return HTTPException(
        status_code=status,
        detail=description,
        headers={"WWW-Authenticate": f'DPoP error="{error}", error_description="{description}"'},
    )


def expected_htu(request: Request) -> str:
    path = request.url.path
    base = os.environ.get("MCP_PUBLIC_BASE_URL")
    if base:
        return base.rstrip("/") + path
    return str(request.url).split("?")[0]


# --------------------------------------------------------------------------- DPoP
def verify_dpop_proof(request: Request, dpop_proof: str, access_token: str | None = None) -> str:
    """Valida la prueba DPoP y devuelve el thumbprint (jkt) de la llave del cliente."""
    try:
        header = jwt.get_unverified_header(dpop_proof)
    except jwt.PyJWTError:
        raise _auth_error(400, "invalid_dpop_proof", "DPoP proof mal formado")

    if header.get("typ") != "dpop+jwt":
        raise _auth_error(400, "invalid_dpop_proof", "typ debe ser dpop+jwt")
    jwk = header.get("jwk")
    if not isinstance(jwk, dict) or jwk.get("kty") != "EC" or "d" in jwk:
        raise _auth_error(400, "invalid_dpop_proof", "jwk publica EC requerida")

    try:
        public_key = jwt.algorithms.ECAlgorithm.from_jwk(jwk)
        payload = jwt.decode(
            dpop_proof, public_key, algorithms=DPOP_ALGS,
            options={"require": ["jti", "htm", "htu", "iat"], "verify_iat": False},
        )
    except (jwt.PyJWTError, ValueError) as e:
        raise _auth_error(401, "invalid_dpop_proof", f"DPoP proof invalido: {e}")

    if payload["htm"] != request.method or payload["htu"] != expected_htu(request):
        raise _auth_error(401, "invalid_dpop_proof", "htm/htu no coinciden con la peticion")

    now = time.time()
    if abs(now - float(payload["iat"])) > DPOP_IAT_WINDOW:
        raise _auth_error(401, "invalid_dpop_proof", "iat fuera de la ventana permitida")

    if access_token is not None:
        ath = _b64u(hashlib.sha256(access_token.encode()).digest())
        if not hmac.compare_digest(str(payload.get("ath", "")), ath):
            raise _auth_error(401, "invalid_dpop_proof", "ath no coincide con el access token")

    jti = str(payload["jti"])
    with _lock:
        for k in [k for k, exp in _seen_jti.items() if exp < now]:
            del _seen_jti[k]
        if jti in _seen_jti:
            raise _auth_error(401, "invalid_dpop_proof", "jti repetido (replay)")
        _seen_jti[jti] = now + 2 * DPOP_IAT_WINDOW

    return compute_jwk_thumbprint(jwk)


# --------------------------------------------------------------------------- tokens
def create_tokens(username: str, jkt: str | None = None):
    now = int(time.time())
    access = {"sub": username, "iat": now, "exp": now + ACCESS_TTL, "type": "access",
              "scope": GRANTED_SCOPE}
    refresh = {"sub": username, "iat": now, "exp": now + REFRESH_TTL, "type": "refresh",
               "jti": secrets.token_urlsafe(16)}
    if jkt:
        access["cnf"] = {"jkt": jkt}
        refresh["cnf"] = {"jkt": jkt}   # el refresh tambien queda atado a la llave
    with _lock:
        active_sessions[username] = time.time()
    return (jwt.encode(access, SECRET_KEY, algorithm=ALGORITHM),
            jwt.encode(refresh, REFRESH_SECRET_KEY, algorithm=ALGORITHM))


def check_credentials(username: str, password: str) -> bool:
    exp_user = os.environ.get("MCP_AUTH_USERNAME")
    exp_pass = os.environ.get("MCP_AUTH_PASSWORD")
    if not exp_user or not exp_pass:
        raise HTTPException(status_code=500, detail="Servidor sin credenciales configuradas")
    ok_u = hmac.compare_digest(username.encode(), exp_user.encode())
    ok_p = hmac.compare_digest(password.encode(), exp_pass.encode())
    return ok_u and ok_p


def touch_session(username: str) -> None:
    """Valida inactividad y renueva la marca de actividad."""
    now = time.time()
    with _lock:
        last = active_sessions.get(username)
        if last is None:
            raise _auth_error(401, "invalid_token", "Sesion no encontrada o cerrada")
        if now - last > IDLE_TIMEOUT:
            del active_sessions[username]
            raise _auth_error(401, "invalid_token", "Sesion cerrada por inactividad")
        active_sessions[username] = now


def verify_access_token(request: Request) -> dict:
    """Exige 'Authorization: DPoP <token>' + cabecera DPoP. Un Bearer simple se rechaza."""
    auth = request.headers.get("Authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "dpop" or not token:
        raise _auth_error(401, "invalid_token", "Se requiere Authorization: DPoP <token>")
    proof = request.headers.get("DPoP")
    if not proof:
        raise _auth_error(401, "invalid_token", "Falta el encabezado DPoP")

    request_jkt = verify_dpop_proof(request, proof, access_token=token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                             options={"require": ["exp", "sub"]})
    except jwt.ExpiredSignatureError:
        raise _auth_error(401, "invalid_token", "Access token expirado, use el refresh token")
    except jwt.PyJWTError:
        raise _auth_error(401, "invalid_token", "Token no valido")

    if payload.get("type") != "access":
        raise _auth_error(401, "invalid_token", "Tipo de token invalido")
    if payload.get("cnf", {}).get("jkt") != request_jkt:
        raise _auth_error(401, "invalid_token", "El token no pertenece a esta llave (DPoP)")
    if REQUIRED_SCOPE not in str(payload.get("scope", "")).split():
        raise _auth_error(403, "insufficient_scope", f"Falta el scope {REQUIRED_SCOPE}")

    touch_session(payload["sub"])
    return payload
