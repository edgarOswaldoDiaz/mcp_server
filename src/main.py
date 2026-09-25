from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks, Depends, status
from typing import Optional
import httpx

from src.config import settings
from src.schemas import JSONRPCRequest, JSONRPCResponse, JSONRPCError, Message
from src.mcp_service import MCPService
from src.orchestrator import orchestrator

mcp_client_session: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_client_session
    mcp_client_session = httpx.AsyncClient()
    yield
    await mcp_client_session.aclose()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

def get_mcp_service() -> MCPService:
    if not mcp_client_session:
        raise RuntimeError("HTTP Session uninitialized")
    return MCPService(mcp_client_session)

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