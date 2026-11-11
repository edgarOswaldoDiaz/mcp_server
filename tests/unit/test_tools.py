from src.mcp.server.main import create_server
from src.mcp.server.tools import _safe_call
from src.mcp.services.object_key import InvalidObjectKey
from src.mcp.services.calculator_service import add_numbers

def test_server_creation():
    # La autenticacion real (OAuth+DPoP) se prueba en test_oauth_dpop_flow.py; aqui solo el armado.
    server = create_server(use_auth=False)
    assert server is not None

def test_add_tool_logic():
    # Prueba unitaria de la lógica de la herramienta de suma
    result = add_numbers(10, 20)
    assert result == {"result": 30}


def test_invalid_object_key_uses_standard_error_envelope():
    def fail_with_invalid_key():
        raise InvalidObjectKey("Clave inválida")

    result = _safe_call(fail_with_invalid_key)

    assert result == {
        "ok": False,
        "error": {
            "code": "INVALID_OBJECT_KEY",
            "message": "Clave inválida",
        },
    }
