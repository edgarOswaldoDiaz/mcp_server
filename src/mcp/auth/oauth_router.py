import time

import jwt
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.mcp.auth import oauth_handler as h

router = APIRouter(prefix="/oauth", tags=["OAuth 2.0 Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def _require_proof(request: Request) -> str:
    proof = request.headers.get("DPoP")
    if not proof:
        raise HTTPException(status_code=400, detail="Falta el encabezado DPoP")
    return h.verify_dpop_proof(request, proof)


@router.post("/token")
def login_for_access_token(request: Request, form_data: LoginRequest):
    jkt = _require_proof(request)
    if not h.check_credentials(form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    access, refresh = h.create_tokens(form_data.username, jkt=jkt)
    return {"access_token": access, "refresh_token": refresh, "token_type": "DPoP",
            "expires_in": h.ACCESS_TTL, "scope": h.GRANTED_SCOPE}


@router.post("/refresh")
def refresh_token_endpoint(request: Request, body: RefreshRequest):
    jkt = _require_proof(request)           # el refresh tambien exige prueba de posesion
    try:
        payload = jwt.decode(body.refresh_token, h.REFRESH_SECRET_KEY, algorithms=[h.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh expirado: login completo requerido")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Refresh token invalido")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="No es un refresh token")
    if payload.get("cnf", {}).get("jkt") != jkt:
        raise HTTPException(status_code=401, detail="El refresh token no pertenece a esta llave")

    username = payload["sub"]
    h.touch_session(username)               # si estuvo inactivo, ya no hay renovacion: login de nuevo

    now = int(time.time())
    access = jwt.encode(
        {"sub": username, "iat": now, "exp": now + h.ACCESS_TTL, "type": "access",
         "scope": h.GRANTED_SCOPE, "cnf": {"jkt": jkt}},   # <- mismo binding que en el login
        h.SECRET_KEY, algorithm=h.ALGORITHM)
    return {"access_token": access, "token_type": "DPoP", "expires_in": h.ACCESS_TTL,
            "scope": h.GRANTED_SCOPE}
