from src.mcp.server.main import create_server
from src.mcp.services.calculator_service import add_numbers

def test_server_creation():
    # Inicialización del servidor MCP configurado con OAuth/DPoP
    server = create_server(use_auth=True)
    assert server is not None

def test_add_tool_logic():
    # Prueba unitaria de la lógica de la herramienta de suma
    result = add_numbers(10, 20)
    assert result == {"result": 30}