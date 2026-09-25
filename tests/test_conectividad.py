import requests
 
class TestAgentCard:
 
    def test_status_code_200(self, base_url):
        resp = requests.get(f"{base_url}/.well-known/agent-card.json", timeout=10)
        assert resp.status_code == 200
 
    def test_no_requiere_autenticacion(self, base_url, no_auth_headers):
        resp = requests.get(f"{base_url}/.well-known/agent-card.json", headers=no_auth_headers, timeout=10)
        assert resp.status_code == 200
 
    def test_estructura_del_card(self, base_url):
        data = requests.get(f"{base_url}/.well-known/agent-card.json", timeout=10).json()
        for campo in ("name", "description", "version", "capabilities", "securitySchemes", "securityRequirements"):
            assert campo in data, f"Falta el campo obligatorio '{campo}'"
        assert isinstance(data["capabilities"], list) and len(data["capabilities"]) > 0
        assert data["securitySchemes"]["bearerAuth"]["scheme"] == "bearer"
 
 
class TestEnvioDeMensaje:
 
    def test_envio_valido_devuelve_200(self, base_url, valid_headers, make_rpc_payload, make_message):
        payload = make_rpc_payload(message=make_message())
        resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10)
        assert resp.status_code == 200
 
    def test_envelope_jsonrpc_correcto(self, base_url, valid_headers, make_rpc_payload, make_message):
        payload = make_rpc_payload(request_id="rpc-envelope-1", message=make_message())
        data = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10).json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "rpc-envelope-1"
        assert data["error"] is None
        assert data["result"] is not None
 
    def test_tarea_creada_con_forma_esperada(self, created_task):
        task = created_task["result"]
        assert task["id"].startswith("task-")
        assert task["contextId"]
        assert task["status"]["state"] == "TASK_STATE_SUBMITTED"
        assert len(task["history"]) == 1
 
    def test_context_id_se_respeta_si_se_envia(self, base_url, valid_headers, make_rpc_payload, make_message):
        payload = make_rpc_payload(message=make_message(contextId="ctx-fijo-001"))
        data = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=10).json()
        assert data["result"]["contextId"] == "ctx-fijo-001"
 
 
class TestPollingDeTareas:
 
    def test_tarea_inexistente_devuelve_404(self, base_url, valid_headers):
        resp = requests.get(f"{base_url}/a2a/tasks/task-no-existe", headers=valid_headers, timeout=10)
        assert resp.status_code == 404
 
    def test_polling_devuelve_el_mismo_task_id(self, base_url, valid_headers, created_task):
        task_id = created_task["result"]["id"]
        resp = requests.get(f"{base_url}/a2a/tasks/{task_id}", headers=valid_headers, timeout=10)
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id
 
    def test_polling_alcanza_estado_terminal(self, base_url, valid_headers, created_task, poll_until_terminal):
        task_id = created_task["result"]["id"]
        final = poll_until_terminal(base_url, valid_headers, task_id)
 
        assert final is not None, "No se obtuvo respuesta durante el polling"
        assert final["status"]["state"] in ("TASK_STATE_COMPLETED", "TASK_STATE_FAILED"), (
            f"La tarea se quedo en '{final['status']['state']}' y no llego a un estado terminal a tiempo"
        )