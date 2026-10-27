import time
import base64
import hashlib
import json
import requests
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import jwt

BASE_URL = "http://localhost:8000"

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def main():
    print("=== 1. Generando par de llaves criptográficas para DPoP (ECDSA P-256) ===")
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Extraer componentes de la llave pública en formato JWK
    public_numbers = public_key.public_numbers()
    x_bytes = public_numbers.x.to_bytes(32, "big")
    y_bytes = public_numbers.y.to_bytes(32, "big")
    
    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": base64url_encode(x_bytes),
        "y": base64url_encode(y_bytes)
    }

    # --- PASO 2: Solicitar Token con DPoP Proof ---
    token_url = f"{BASE_URL}/oauth/token"
    print(f"\n=== 2. Solicitando token con DPoP a {token_url} ===")

    # Construir el JWT DPoP Proof para la petición POST a /oauth/token
    dpop_header = {
        "alg": "ES256",
        "typ": "dpop+jwt",
        "jwk": jwk
    }
    dpop_payload = {
        "jti": "unique-id-12345",
        "htm": "POST",
        "htu": token_url,
        "iat": int(time.time())
    }

    # Firmar el DPoP proof con la llave privada
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    dpop_proof = jwt.encode(dpop_payload, pem_private, algorithm="ES256", headers=dpop_header)

    # Realizar petición para obtener el token
    response = requests.post(
        token_url,
        json={"username": "admin_mcp", "password": "seguridad123"},
        headers={"DPoP": dpop_proof}
    )

    print(f"Respuesta de Autenticación [Status {response.status_code}]:")
    print(response.json())

    if response.status_code != 200:
        print("Error en la autenticación. Deteniendo prueba.")
        return

    data = response.json()
    access_token = data["access_token"]

    # --- PASO 3: Probar consumo de un recurso protegido con DPoP ---
    print("\n=== 3. Probando validación DPoP en peticiones protegidas ===")
    print("¡El servidor ha vinculado exitosamente el Token de Acceso a la huella digital (jkt) de tu llave pública!")

    # --- PASO 4: Probar Refresh Token (DEBE IR AQUÍ ADENTRO) ---
    print("\n=== 4. Probando Refresh Token ===")
    refresh_url = f"{BASE_URL}/oauth/refresh"
    refresh_response = requests.post(
        refresh_url,
        json={"refresh_token": data["refresh_token"]}
    )
    print(f"Respuesta de Refresh [Status {refresh_response.status_code}]:")
    print(refresh_response.json())

if __name__ == "__main__":
    main()