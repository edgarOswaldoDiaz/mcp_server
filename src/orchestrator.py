import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
from src.schemas import Task, TaskState, Status, Artifact, Part, Message
from src.mcp_service import MCPService

class TaskOrchestrator:
    def __init__(self):
        self._store: Dict[str, Task] = {}

    def spawn_task(self, context_id: Optional[str], message: Message) -> Task:
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
        task = self._store.get(task_id)
        if not task:
            return

        self._update_status(task, TaskState.WORKING)

        try:
            payload_text = next((p.text for p in task.history[-1].parts if p.text), "")
            
            mcp_output = await mcp.invoke_tool("process_query", {"query": payload_text})

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
        return self._store.get(task_id)

    def _update_status(self, task: Task, state: TaskState, msg: Optional[str] = None):
        task.status.state = state
        task.status.message = msg
        task.status.timestamp = datetime.now(timezone.utc).isoformat()

orchestrator = TaskOrchestrator()