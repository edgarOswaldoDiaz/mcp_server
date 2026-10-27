import jwt
import datetime
import json
import hashlib
import base64
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "tu_clave_secreta_super_segura_mcp"
REFRESH_SECRET_KEY = "tu_clave_refresh_secret_mcp"
ALGORITHM = "HS256"

# Diccionario en memoria para controlar la última actividad por usuario
active_sessions = {}

security = HTTPBearer()

def compute_jwk_thumbprint(jwk: dict) -> str:
    """
    Calcula el JWK Thumbprint (RFC 7638) para vincular la clave al token (DPoP).
    """
    kty = jwk.get("kty")
    if kty == "RSA":
        canonical = {"e": jwk["e"], "kty": "RSA", "n": jwk["n"]}
    elif kty == "EC":
        canonical = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
    else:
        raise HTTPException(status_code=400, detail="Tipo de clave JWK no soportado para DPoP")
    
    json_str = json.dumps(canonical, separators=(",", ":"), sort_keys=True)
    digest = hashlib.sha256(json_str.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")

def create_tokens(username: str, jkt: str = None):
    now = datetime.datetime.utcnow()

    # 1. Access Token (Corta duración: 10 minutos)
    access_payload = {
        "sub": username,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=10),
        "type": "access"
    }
    
    # Vinculación criptográfica DPoP (Binding con el Thumbprint de la llave del cliente)
    if jkt:
        access_payload["cnf"] = {"jkt": jkt}

    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

    # 2. Refresh Token (Larga duración)
    refresh_payload = {
        "sub": username,
        "iat": now,
        "exp": now + datetime.timedelta(days=7),
        "type": "refresh"
    }
    refresh_token = jwt.encode(refresh_payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    # Registrar el timestamp de actividad inicial
    active_sessions[username] = datetime.datetime.utcnow()

    return access_token, refresh_token

def verify_dpop_proof(request: Request, dpop_proof: str):
    """
    Valida el encabezado DPoP (Proof-of-Possession) según la RFC 9449 y retorna el jkt.
    """
    try:
        unverified_header = jwt.get_unverified_header(dpop_proof)
        jwk = unverified_header.get("jwk")
        if not jwk:
            raise HTTPException(status_code=400, detail="DPoP proof sin clave pública (JWK)")

        public_key = jwt.algorithms.ECAlgorithm.from_jwk(jwk) if jwk.get("kty") == "EC" else jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
        
        payload = jwt.decode(
            dpop_proof,
            public_key,
            algorithms=["ES256", "RS256", "PS256"]
        )

        expected_htm = request.method
        expected_htu = str(request.url).split("?")[0]

        if payload.get("htm") != expected_htm or payload.get("htu") != expected_htu:
            raise HTTPException(status_code=400, detail="Claims de DPoP (htm/htu) no coinciden con la petición")

        # Retornar el thumbprint calculado de esta llave
        return compute_jwk_thumbprint(jwk)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"DPoP proof inválido: {str(e)}")

def verify_access_token(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    
    # 1. Obtener y validar cabecera DPoP obligatoria
    dpop_proof = request.headers.get("DPoP")
    if not dpop_proof:
        raise HTTPException(status_code=400, detail="Falta el encabezado DPoP obligatorio")
    
    # 2. Validar DPoP Proof y obtener el jkt de la petición actual
    request_jkt = verify_dpop_proof(request, dpop_proof)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Tipo de token inválido")

        # 3. Validar vinculación DPoP: El jkt del token debe coincidir con la llave usada en la petición
        token_cnf = payload.get("cnf")
        if not token_cnf or token_cnf.get("jkt") != request_jkt:
            raise HTTPException(status_code=401, detail="El DPoP Proof no coincide con la llave vinculada al token")

        username = payload.get("sub")

        # Control de Estado Inactivo (15 minutos sin peticiones)
        if username in active_sessions:
            last_activity = active_sessions[username]
            if datetime.datetime.utcnow() - last_activity > datetime.timedelta(minutes=15):
                del active_sessions[username]
                raise HTTPException(
                    status_code=401,
                    detail="Sesión cerrada por inactividad. Debe volver a solicitar token."
                )
        else:
            raise HTTPException(status_code=401, detail="Sesión no encontrada o expirada")

        active_sessions[username] = datetime.datetime.utcnow()
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token de acceso ha expirado, use el refresh token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token no válido")