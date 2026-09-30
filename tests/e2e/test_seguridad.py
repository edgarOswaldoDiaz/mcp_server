import requests
 
 
class TestAutenticacion:
 
    def test_rpc_sin_token_devuelve_401(self, base_url, no_auth_headers, make_rpc_payload, make_message):
        payload = make_rpc_payload(message=make_message())
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=no_auth_headers, timeout=10)
        assert resp.status_code == 401
 
    def test_rpc_token_invalido_devuelve_401(self, base_url, invalid_headers, make_rpc_payload, make_message):
        payload = make_rpc_payload(message=make_message())
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=invalid_headers, timeout=10)
        assert resp.status_code == 401
 
    def test_tasks_sin_token_devuelve_401(self, base_url, no_auth_headers):
        resp = requests.get(f"{base_url}/a2a/tasks/task-cualquiera", headers=no_auth_headers, timeout=10)
        assert resp.status_code == 401
 
    def test_tasks_token_invalido_devuelve_401(self, base_url, invalid_headers):
        resp = requests.get(f"{base_url}/a2a/tasks/task-cualquiera", headers=invalid_headers, timeout=10)
        assert resp.status_code == 401
 
    def test_header_sin_prefijo_bearer_devuelve_401(self, base_url):
        """Enviar el token pelado, sin el prefijo 'Bearer ', debe rechazarse."""
        headers = {"Authorization": "secret-a2a-token-123", "Content-Type": "application/json"}
        resp = requests.get(f"{base_url}/a2a/tasks/task-cualquiera", headers=headers, timeout=10)
        assert resp.status_code == 401
 
    def test_esquema_basic_devuelve_401(self, base_url):
        """Un esquema distinto a Bearer (ej. Basic) debe ser rechazado."""
        headers = {"Authorization": "Basic dXNlcjpwYXNz", "Content-Type": "application/json"}
        resp = requests.get(f"{base_url}/a2a/tasks/task-cualquiera", headers=headers, timeout=10)
        assert resp.status_code == 401
 
 
class TestErroresJSONRPC:
 
    def test_metodo_no_soportado_devuelve_error_32601(self, base_url, valid_headers, make_rpc_payload, make_message):
        payload = make_rpc_payload(method="message/unsupported", message=make_message())
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10)
 
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] is None
        assert data["error"]["code"] == -32601
 
    def test_metodo_no_soportado_no_genera_tarea(self, base_url, valid_headers, make_rpc_payload, make_message):
        payload = make_rpc_payload(method="message/unsupported", message=make_message())
        data = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10).json()
        assert data["result"] is None
 
    def test_params_sin_message_devuelve_error_32602(self, base_url, valid_headers, make_rpc_payload):
        payload = make_rpc_payload(message=None)
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] is None
        assert data["error"]["code"] == -32602