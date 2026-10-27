from src.oauth_client import DPoPA2AClient

def probar_firma_local():
    print("inicializando cliente DPoP y generando par de llaves ECDSA P-256...")
    client = DPoPA2AClient()
    
    # Probamos generar una prueba DPoP firmada
    proof = client._create_dpop_proof("POST", "http://localhost:8000/oauth/token")
    
    print("Firma DPoP generada con exito")
    print("JWT DPoP (primeros caracteres):", proof[:60] + "...")

if __name__ == "__main__":
    probar_firma_local()