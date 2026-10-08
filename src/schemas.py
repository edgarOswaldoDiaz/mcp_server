from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

class TaskState(str, Enum):
    SUBMITTED = "TASK_STATE_SUBMITTED"
    WORKING = "TASK_STATE_WORKING"
    INPUT_REQUIRED = "TASK_STATE_INPUT_REQUIRED"
    AUTH_REQUIRED = "TASK_STATE_AUTH_REQUIRED"
    COMPLETED = "TASK_STATE_COMPLETED"
    FAILED = "TASK_STATE_FAILED"
    CANCELED = "TASK_STATE_CANCELED"
    REJECTED = "TASK_STATE_REJECTED"

class Status(BaseModel):
    state: TaskState
    message: Optional[str] = None
    timestamp: str

class Part(BaseModel):
    text: Optional[str] = None
    raw: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class Artifact(BaseModel):
    artifactId: str
    name: str
    description: Optional[str] = None
    parts: List[Part]

class Message(BaseModel):
    messageId: str
    contextId: Optional[str] = None
    taskId: Optional[str] = None
    role: str
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = None

class Task(BaseModel):
    id: str
    contextId: str
    status: Status
    artifacts: List[Artifact] = []
    history: List[Message] = []

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Dict[str, Any]

class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None