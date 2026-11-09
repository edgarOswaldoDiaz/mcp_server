import json
import time
import uuid
import pytest
import requests


ATAQUES = [
    "../metadatos/ingresos_sinteticos.json",
    "../../etc/passwd",
    "metadatos/../../etc/passwd",
    "/etc/passwd",
    r"..\..\etc\passwd",
    "%2e%2e/%2e%2e/etc/passwd",
    "%252e%252e/%252e%252e/etc/passwd",
    "..%2f..%2fetc%2fpasswd",
    "..%5c..%5cetc%5cpasswd",
    "metadatos/%2e%2e/%2e%2e/etc/passwd",
]


@pytest.mark.parametrize("ruta", ATAQUES)
def test_traversal_rechazado_sin_exponer_datos(
    ruta, base_url, valid_headers
):
    identificador = uuid.uuid4().hex

    payload = {
        "jsonrpc": "2.0",
        "id": identificador,
        "method": "message/send",
        "params": {
            "message": {
                "messageId": identificador,
                "role": "user",
                "parts": [{"text": f"leer {ruta}"}],
            }
        },
    }

    respuesta = requests.post(
        f"{base_url}/a2a/rpc",
        json=payload,
        headers=valid_headers,
        timeout=10,
    )

    assert respuesta.status_code == 200, respuesta.text

    task_id = respuesta.json()["result"]["id"]
    tarea = None

    for _ in range(30):
        consulta = requests.get(
            f"{base_url}/a2a/tasks/{task_id}",
            headers=valid_headers,
            timeout=10,
        )

        assert consulta.status_code == 200
        tarea = consulta.json()

        estado = tarea["status"]["state"]

        if estado in ("TASK_STATE_COMPLETED", "TASK_STATE_FAILED"):
            break

        time.sleep(1)

    assert tarea is not None
    assert tarea["status"]["state"] == "TASK_STATE_FAILED", (
        f"La ruta peligrosa no fue rechazada: {ruta}. "
        f"Respuesta: {json.dumps(tarea, ensure_ascii=False)}"
    )

    assert not tarea.get("artifacts"), (
        f"La solicitud rechazada devolvió artefactos: {ruta}"
    )

    contenido = json.dumps(tarea, ensure_ascii=False).lower()

    assert "root:x:0:0" not in contenido
    assert "daemon:x:" not in contenido
