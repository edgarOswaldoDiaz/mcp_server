
"""
Pruebas E2E de seguridad de la API A2A.

Comprueban el rechazo de solicitudes sin autenticación válida
y el manejo de errores en las peticiones JSON-RPC.
"""
import requests


class TestAutenticacion:
    """Verifica que los endpoints protegidos exijan autenticación válida."""
    def test_rpc_sin_token_devuelve_401(self, base_url, no_auth_headers, make_rpc_payload, make_message):
        """Comprueba que enviar un mensaje sin token sea rechazado."""
        payload = make_rpc_payload(message=make_message())
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=no_auth_headers, timeout=10)
        assert resp.status_code == 401

    def test_rpc_token_invalido_devuelve_401(self, base_url, invalid_headers, make_rpc_payload, make_message):
        """Comprueba que un token inválido no permita enviar mensajes."""
        payload = make_rpc_payload(message=make_message())
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=invalid_headers, timeout=10)
        assert resp.status_code == 401

    def test_tasks_sin_token_devuelve_401(self, base_url, no_auth_headers):
        """Verifica que consultar tareas sin token sea rechazado."""
        resp = requests.get(f"{base_url}/a2a/tasks/task-cualquiera", headers=no_auth_headers, timeout=10)
        assert resp.status_code == 401

    def test_tasks_token_invalido_devuelve_401(self, base_url, invalid_headers):
        """Verifica que un token inválido no permita consultar tareas."""
        resp = requests.get(f"{base_url}/a2a/tasks/task-cualquiera", headers=invalid_headers, timeout=10)
        assert resp.status_code == 401

    def test_header_sin_prefijo_bearer_devuelve_401(self, base_url):
        """Comprueba que el encabezado incluya el prefijo 'Bearer '."""
        headers = {"Authorization": "secret-a2a-token-123", "Content-Type": "application/json"}
        resp = requests.get(f"{base_url}/a2a/tasks/task-cualquiera", headers=headers, timeout=10)
        assert resp.status_code == 401

    def test_esquema_basic_devuelve_401(self, base_url):
        """Comprueba que se rechace Basic cuando se espera Bearer."""
        headers = {"Authorization": "Basic dXNlcjpwYXNz", "Content-Type": "application/json"}
        resp = requests.get(f"{base_url}/a2a/tasks/task-cualquiera", headers=headers, timeout=10)
        assert resp.status_code == 401

class TestErroresJSONRPC:
    """Comprueba las respuestas ante solicitudes JSON-RPC incorrectas."""
    def test_metodo_no_soportado_devuelve_error_32601(self, base_url, valid_headers, make_rpc_payload, make_message):
        """Verifica el error -32601 cuando el método no está soportado."""
        payload = make_rpc_payload(method="message/unsupported", message=make_message())
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10)
        # JSON-RPC puede comunicar el error en el cuerpo con HTTP 200.
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] is None
        assert data["error"]["code"] == -32601

    def test_metodo_no_soportado_no_genera_tarea(self, base_url, valid_headers, make_rpc_payload, make_message):
        """Comprueba que un método no reconocido no devuelva una tarea."""
        payload = make_rpc_payload(method="message/unsupported", message=make_message())
        data = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10).json()
        assert data["result"] is None

    def test_params_sin_message_devuelve_error_32602(self, base_url, valid_headers, make_rpc_payload):
        """Verifica el error -32602 cuando faltan los parámetros requeridos."""
        payload = make_rpc_payload(message=None)
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] is None
        assert data["error"]["code"] == -32602