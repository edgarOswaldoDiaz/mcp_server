from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import jwt
import datetime
from src.mcp.auth.oauth_handler import (
    create_tokens, 
    verify_dpop_proof, 
    REFRESH_SECRET_KEY, 
    ALGORITHM, 
    active_sessions, 
    SECRET_KEY
)

router = APIRouter(prefix="/oauth", tags=["OAuth 2.0 Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/token")
def login_for_access_token(request: Request, form_data: LoginRequest):
    # 1. Validar credenciales
    if form_data.username != "admin_mcp" or form_data.password != "seguridad123":
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    
    # 2. Extraer y validar el encabezado DPoP obligatorio para la emisión del token vinculado
    dpop_proof = request.headers.get("DPoP")
    if not dpop_proof:
        raise HTTPException(status_code=400, detail="Falta el encabezado DPoP obligatorio para obtener el token")
    
    # 3. Validar el proof y obtener el jkt (Thumbprint) de la llave del cliente
    jkt = verify_dpop_proof(request, dpop_proof)

    # 4. Crear los tokens vinculando el jkt en el access_token
    access_token, refresh_token = create_tokens(form_data.username, jkt=jkt)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "DPoP"
    }

@router.post("/refresh")
def refresh_token_endpoint(body: RefreshRequest):
    try:
        # Validar el Refresh Token de larga duración
        payload = jwt.decode(body.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="El token proporcionado no es un refresh token")

        username = payload.get("sub")

        # Generar un nuevo Access Token automáticamente sin pedir contraseña
        now = datetime.datetime.utcnow()
        new_access_payload = {
            "sub": username,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=10),
            "type": "access"
        }
        new_access_token = jwt.encode(new_access_payload, SECRET_KEY, algorithm=ALGORITHM)

        # Renovar el registro de actividad para evitar el cierre por inactividad
        active_sessions[username] = datetime.datetime.utcnow()

        return {
            "access_token": new_access_token,
            "token_type": "DPoP"
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El refresh token ha expirado. Autenticación completa requerida.")
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token inválido")