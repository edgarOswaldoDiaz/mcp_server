from src.mcp.server.main import create_server

def test_create_server():
    # La autenticacion real (OAuth+DPoP) se prueba en test_oauth_dpop_flow.py; aqui solo el armado.
    server = create_server(use_auth=False)
    assert server is not None