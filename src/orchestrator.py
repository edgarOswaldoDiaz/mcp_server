"""Orquestador de tareas del agente A2A.

Crea las tareas, las ejecuta contra el servidor MCP mediante mcp-network y mantiene su estado.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
from .schemas import Task, TaskState, Status, Artifact, Part, Message
from .mcp_service import DPoPClientService as MCPService

class TaskOrchestrator:
    """Gestiona el ciclo de vida de las tareas del agente."""

    def __init__(self):
        self._store: Dict[str, Task] = {}

    def spawn_task(self, context_id: Optional[str], message: Message) -> Task:
        """Crea y registra una tarea nueva en estado TASK_STATE_SUBMITTED."""
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        ctx = context_id or f"ctx-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()

        task = Task(
            id=task_id,
            contextId=ctx,
            status=Status(state=TaskState.SUBMITTED, timestamp=now),
            history=[message]
        )
        self._store[task_id] = task
        return task

    async def execute_workflow(self, task_id: str, mcp: MCPService) -> None:
        """Ejecuta la tarea llamando a las herramientas en el MCP con autenticacion OAuth+DPoP (ver mcp_service)."""
        task = self._store.get(task_id)
        if not task:
            return

        self._update_status(task, TaskState.WORKING)

        try:
            payload_text = next((p.text for p in task.history[-1].parts if p.text), "")

            # "leer <ruta>" -> lectura de un archivo del bucket confidencial (solo lectura).
            # Cualquier otro texto conserva el comportamiento anterior (echo).
            if payload_text.strip().lower().startswith("leer "):
                key = payload_text.strip()[5:].strip()
                tool = self._read_tool_for(key)
                if tool is None:
                    raise ValueError(f"Extension no soportada para '{key}' (use .json o .parquet)")
                mcp_output = await mcp.invoke_tool(tool, {"object_key": key})
            else:
                mcp_output = await mcp.invoke_tool("echo", {"message": payload_text})

            if not isinstance(mcp_output, dict):   # Part.data solo admite diccionarios
                mcp_output = {"result": mcp_output}

            artifact = Artifact(
                artifactId=f"art-{uuid.uuid4().hex[:6]}",
                name="execution_result",
                parts=[Part(data=mcp_output)]
            )
            task.artifacts.append(artifact)
            self._update_status(task, TaskState.COMPLETED, "Execution finished successfully with DPoP")

        except Exception as err:
            self._update_status(task, TaskState.FAILED, f"Execution halted: {str(err)}")

    @staticmethod
    def _read_tool_for(key: str) -> Optional[str]:
        """Elige la herramienta de lectura del MCP segun la ruta del objeto."""
        k = key.lower()
        if k.endswith(".json"):
            return "read_minio_json"
        if k.endswith(".parquet"):
            return "read_minio_geoparquet" if k.startswith("geo/") else "read_minio_parquet"
        return None

    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Busca una tarea por su identificador."""
        return self._store.get(task_id)

    def _update_status(self, task: Task, state: TaskState, msg: Optional[str] = None):
        """Actualiza el estado, mensaje y timestamp de la tarea."""
        task.status.state = state
        task.status.message = msg
        task.status.timestamp = datetime.now(timezone.utc).isoformat()

orchestrator = TaskOrchestrator()