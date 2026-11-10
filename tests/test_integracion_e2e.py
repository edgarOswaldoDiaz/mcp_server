
"""
Pruebas E2E de integración A2A -> MCP -> RustFS.

Comprueban echo y la lectura de los tres tipos de objetos
sintéticos disponibles en el almacenamiento.
"""

import uuid
import requests
import pytest

def ejecutar_tarea(
    texto,
    base_url,
    valid_headers,
    make_rpc_payload,
    make_message,
    poll_until_terminal,
):
    payload = make_rpc_payload(
        request_id=f"qa-e2e-{uuid.uuid4().hex}",
        message=make_message(text=texto),
    )

    response = requests.post(
        f"{base_url}/a2a/rpc",
        json=payload,
        headers=valid_headers,
        timeout=10,
    )

    assert response.status_code == 200, response.text

    body = response.json()
    assert body.get("error") is None, body
    assert body.get("result") is not None, body

    task_id = body["result"]["id"]

    final = poll_until_terminal(
        base_url,
        valid_headers,
        task_id,
    )

    assert final is not None, f"No terminó la tarea {task_id}"

    return final


def test_integracion_echo(
    base_url,
    valid_headers,
    make_rpc_payload,
    make_message,
    poll_until_terminal,
):
    mensaje = f"qa-integracion-{uuid.uuid4().hex}"

    final = ejecutar_tarea(
        mensaje,
        base_url,
        valid_headers,
        make_rpc_payload,
        make_message,
        poll_until_terminal,
    )

    assert final["status"]["state"] == "TASK_STATE_COMPLETED"
    assert final.get("artifacts"), "Echo no produjo artefactos"
    assert mensaje in str(final["artifacts"])


@pytest.mark.parametrize(
    "ruta,contenido_esperado",
    [
        (
            "metadatos/ingresos_sinteticos.json",
            "ingresos_sinteticos",
        ),
        (
            "ingresos/ingresos_sinteticos.parquet",
            None,
        ),
        (
            "geo/puntos_sinteticos.parquet",
            None,
        ),
    ],
)
def test_lectura_de_objetos_rustfs(
    ruta,
    contenido_esperado,
    base_url,
    valid_headers,
    make_rpc_payload,
    make_message,
    poll_until_terminal,
):
    final = ejecutar_tarea(
        f"leer {ruta}",
        base_url,
        valid_headers,
        make_rpc_payload,
        make_message,
        poll_until_terminal,
    )

    assert final["status"]["state"] == "TASK_STATE_COMPLETED", (
        f"No se pudo leer {ruta}. "
        f"Estado: {final['status']}"
    )

    artifacts = final.get("artifacts", [])

    assert artifacts, f"La lectura de {ruta} no generó artefactos"

    if contenido_esperado:
        assert contenido_esperado in str(artifacts), (
            f"No se encontró el contenido esperado en {ruta}: {artifacts}"
        )


def test_objeto_inexistente_falla_sin_artefactos(
    base_url,
    valid_headers,
    make_rpc_payload,
    make_message,
    poll_until_terminal,
):
    ruta = f"metadatos/no_existe_{uuid.uuid4().hex}.json"

    final = ejecutar_tarea(
        f"leer {ruta}",
        base_url,
        valid_headers,
        make_rpc_payload,
        make_message,
        poll_until_terminal,
    )

    assert final["status"]["state"] == "TASK_STATE_FAILED"
    assert not final.get("artifacts")
