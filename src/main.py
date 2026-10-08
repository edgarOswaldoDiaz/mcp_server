from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks, Depends, status
from .config import settings
from .schemas import JSONRPCRequest, JSONRPCResponse, JSONRPCError, Message  
from .mcp_service import MCPService
from .orchestrator import orchestrator

app = FastAPI(title=settings.app_name)

def get_mcp_service() -> MCPService:
    return MCPService()

def authenticate(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication scheme"
        )
    token = authorization.split(" ")[1]
    if token != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access"
        )
    return token

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    return {
        "name": settings.app_name,
        "description": "Enterprise A2A Protocol Implementation Node",
        "version": "1.0.0",
        "capabilities": ["text-processing", "mcp-execution"],
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer"}
        },
        "securityRequirements": [{"bearerAuth": []}]
    }


@app.post("/a2a/rpc", response_model=JSONRPCResponse)
async def dispatch_rpc(
    request: JSONRPCRequest,
    background_tasks: BackgroundTasks,
    mcp: MCPService = Depends(get_mcp_service),
    _: str = Depends(authenticate)
):
    if request.method != "message/send":
        return JSONRPCResponse(
            id=request.id,
            error=JSONRPCError(code=-32601, message="Method unsupported")
        )

    raw_msg = request.params.get("message")
    if not raw_msg:
        return JSONRPCResponse(
            id=request.id,
            error=JSONRPCError(code=-32602, message="Invalid params: 'message' required")
        )

    msg = Message(**raw_msg)
    task = orchestrator.spawn_task(msg.contextId, msg)
    
    background_tasks.add_task(orchestrator.execute_workflow, task.id, mcp)

    return JSONRPCResponse(id=request.id, result=task.dict())

@app.get("/a2a/tasks/{task_id}")
async def fetch_task(task_id: str, _: str = Depends(authenticate)):
    task = orchestrator.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task ID not found")
    return task