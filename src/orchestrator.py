"""Orquestador de tareas del agente A2A.

Crea las tareas, las ejecuta contra el servidor MCP y lleva su estado.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
from .schemas import Task, TaskState, Status, Artifact, Part, Message
from .mcp_service import MCPService

class TaskOrchestrator:
    """Gestiona el ciclo de vida de las tareas del agente.

    Guarda las tareas en memoria (se pierden al reiniciar el contenedor) y
    ejecuta cada una contra el servidor MCP.
    """
    def __init__(self):
        """Crea el almacén en memoria de tareas, indexado por id.
        """
        self._store: Dict[str, Task] = {}

    def spawn_task(self, context_id: Optional[str], message: Message) -> Task:
        """Crea y registra una tarea nueva en estado TASK_STATE_SUBMITTED.

        Genera el id ("task-" más 8 caracteres hexadecimales) y, si no se recibe,
        el contexto ("ctx-" más 8 caracteres hexadecimales).

        Args:
            context_id: contexto de la conversación, o None para crear uno nuevo.
            message: mensaje del cliente, queda como primer elemento del historial.

        Returns:
            Task: la tarea registrada.
        """
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
        """Ejecuta la tarea contra el servidor MCP (se lanza en segundo plano).

        Pasa la tarea a WORKING, toma el primer texto del último mensaje del
        historial y lo envía a la herramienta "echo" del MCP. El resultado se
        guarda como artefacto "execution_result" y la tarea termina en COMPLETED.
        Cualquier excepción deja la tarea en FAILED con el motivo en el mensaje.
        Si el id no existe, no hace nada.

        Args:
            task_id: identificador de la tarea a ejecutar.
            mcp: servicio que invoca las herramientas del servidor MCP.
        """
        task = self._store.get(task_id)
        if not task:
            return

        self._update_status(task, TaskState.WORKING)

        try:
            payload_text = next((p.text for p in task.history[-1].parts if p.text), "")
            
            mcp_output = await mcp.invoke_tool("echo", {"message": payload_text})

            artifact = Artifact(
                artifactId=f"art-{uuid.uuid4().hex[:6]}",
                name="execution_result",
                parts=[Part(data=mcp_output)]
            )
            task.artifacts.append(artifact)
            self._update_status(task, TaskState.COMPLETED, "Execution finished successfully")

        except Exception as err:
            self._update_status(task, TaskState.FAILED, f"Execution halted: {str(err)}")

    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Busca una tarea por su identificador.

        Returns:
            Optional[Task]: la tarea, o None si no existe.
        """
        return self._store.get(task_id)

    def _update_status(self, task: Task, state: TaskState, msg: Optional[str] = None):
        """Actualiza el estado, el mensaje y la marca de tiempo (UTC, ISO 8601) de la tarea.

        Args:
            task: tarea a modificar.
            state: nuevo estado.
            msg: detalle opcional del estado (por ejemplo, el motivo de un fallo).
        """
        task.status.state = state
        task.status.message = msg
        task.status.timestamp = datetime.now(timezone.utc).isoformat()

orchestrator = TaskOrchestrator()