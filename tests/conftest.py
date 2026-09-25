import os
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get("A2A_BASE_URL", "http://localhost:8000")
VALID_TOKEN = os.environ.get("A2A_API_KEY", "secret-a2a-token-123")
INVALID_TOKEN = "token-invalido-000-fake"
REQUEST_TIMEOUT = float(os.environ.get("A2A_REQUEST_TIMEOUT", "10"))
POLL_TIMEOUT = float(os.environ.get("A2A_POLL_TIMEOUT", "30"))
POLL_INTERVAL = float(os.environ.get("A2A_POLL_INTERVAL", "1"))

TERMINAL_STATES = {"TASK_STATE_COMPLETED", "TASK_STATE_FAILED"}

@pytest.fixture(scope="session", autouse=True)
def ensure_server_is_up():
    try:
        resp = requests.get(f"{BASE_URL}/.well-known/agent-card.json", timeout=5)
    except requests.exceptions.RequestException as exc:
        pytest.exit(
            f"No se pudo conectar a {BASE_URL}. Verifica que el servicio "
            f"(uvicorn / contenedor Docker) este corriendo. Detalle: {exc}",
            returncode=1,
        )
    if resp.status_code >= 500:
        pytest.exit(
            f"El servidor respondio {resp.status_code} en {BASE_URL}. "
            "Revisa los logs del contenedor antes de correr las pruebas.",
            returncode=1,
        )


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def valid_headers() -> dict:
    return {"Authorization": f"Bearer {VALID_TOKEN}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def invalid_headers() -> dict:
    return {"Authorization": f"Bearer {INVALID_TOKEN}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def no_auth_headers() -> dict:
    return {"Content-Type": "application/json"}


def _build_message(text: str = "Hola agente, ejecuta process_query", **overrides) -> dict:
    message = {
        "messageId": f"msg-{uuid.uuid4().hex[:8]}",
        "role": "user",
        "parts": [{"text": text}],
    }
    message.update(overrides)
    return message


def _build_rpc_payload(method: str = "message/send", message: dict = None, request_id="test-1") -> dict:
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": {}}
    if message is not None:
        payload["params"]["message"] = message
    return payload


@pytest.fixture
def make_message():
    return _build_message

@pytest.fixture
def make_rpc_payload():
    return _build_rpc_payload

def _poll_until_terminal(base_url, headers, task_id, timeout=POLL_TIMEOUT, interval=POLL_INTERVAL):
    deadline = time.time() + timeout
    last_task = None
    while time.time() < deadline:
        resp = requests.get(f"{base_url}/a2a/tasks/{task_id}", headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        last_task = resp.json()
        if last_task["status"]["state"] in TERMINAL_STATES:
            return last_task
        time.sleep(interval)
    return last_task


@pytest.fixture
def poll_until_terminal():
    return _poll_until_terminal

@pytest.fixture
def created_task(base_url, valid_headers, make_rpc_payload, make_message):
    payload = make_rpc_payload(message=make_message())
    resp = requests.post(f"{base_url}/a2a/rpc", json=payload, headers=valid_headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()