from src.mcp.server.main import create_server

def test_create_server():
    # Se valida la inicialización con la autenticación activada por defecto o explícita
    server = create_server(use_auth=True)
    assert server is not None