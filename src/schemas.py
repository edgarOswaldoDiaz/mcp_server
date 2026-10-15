"""Modelos de datos (Pydantic) del agente A2A.

Definen los mensajes, las tareas y sus estados según el protocolo A2A,
y los sobres de petición y respuesta de JSON-RPC 2.0.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

class TaskState(str, Enum):
    """Estados posibles de una tarea (valores TASK_STATE_*).

    Attributes:
        SUBMITTED: tarea recibida, aún sin procesar.
        WORKING: tarea en ejecución.
        INPUT_REQUIRED: espera más información del cliente.
        AUTH_REQUIRED: requiere autenticación adicional.
        COMPLETED: terminó con éxito.
        FAILED: terminó con error.
        CANCELED: tarea cancelada.
        REJECTED: rechazada por el agente.
    """
    SUBMITTED = "TASK_STATE_SUBMITTED"
    WORKING = "TASK_STATE_WORKING"
    INPUT_REQUIRED = "TASK_STATE_INPUT_REQUIRED"
    AUTH_REQUIRED = "TASK_STATE_AUTH_REQUIRED"
    COMPLETED = "TASK_STATE_COMPLETED"
    FAILED = "TASK_STATE_FAILED"
    CANCELED = "TASK_STATE_CANCELED"
    REJECTED = "TASK_STATE_REJECTED"

class Status(BaseModel):
    """Estado de una tarea en un momento dado.

    Attributes:
        state: estado actual (TaskState).
        message: texto opcional con el detalle o el error.
        timestamp: marca de tiempo del cambio de estado.
    """
    state: TaskState
    message: Optional[str] = None
    timestamp: str

class Part(BaseModel):
    """Fragmento de contenido de un mensaje o artefacto; se usa uno de sus campos.

    Attributes:
        text: texto plano.
        raw: contenido binario codificado como cadena.
        url: enlace al contenido.
        data: datos estructurados (JSON).
    """
    text: Optional[str] = None
    raw: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class Artifact(BaseModel):
    """Resultado producido por una tarea.

    Attributes:
        artifactId: identificador del artefacto.
        name: nombre del artefacto.
        description: descripción opcional.
        parts: contenido, como lista de Part.
    """
    artifactId: str
    name: str
    description: Optional[str] = None
    parts: List[Part]

class Message(BaseModel):
    """Mensaje intercambiado entre el cliente y el agente.

    Attributes:
        messageId: identificador del mensaje.
        contextId: identificador de la conversación (opcional).
        taskId: tarea a la que pertenece (opcional).
        role: rol del emisor del mensaje.
        parts: contenido, como lista de Part.
        metadata: datos adicionales opcionales.
    """
    messageId: str
    contextId: Optional[str] = None
    taskId: Optional[str] = None
    role: str
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = None

class Task(BaseModel):
    """Unidad de trabajo del agente y su estado.

    Attributes:
        id: identificador de la tarea.
        contextId: identificador del contexto.
        status: estado actual (Status).
        artifacts: resultados producidos.
        history: mensajes asociados a la tarea.
    """
    id: str
    contextId: str
    status: Status
    artifacts: List[Artifact] = []
    history: List[Message] = []

class JSONRPCRequest(BaseModel):
    """Solicitud JSON-RPC 2.0 recibida en POST /a2a/rpc.

    Attributes:
        jsonrpc: versión del protocolo ("2.0").
        id: identificador de la solicitud, se repite en la respuesta.
        method: método invocado (por ejemplo message/send).
        params: parámetros del método.
    """
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Dict[str, Any]

class JSONRPCError(BaseModel):
    """Error dentro de una respuesta JSON-RPC.

    Attributes:
        code: código numérico (por ejemplo -32601 método no soportado, -32602 parámetros inválidos).
        message: descripción del error.
        data: información adicional opcional.
    """
    code: int
    message: str
    data: Optional[Any] = None

class JSONRPCResponse(BaseModel):
    """Respuesta JSON-RPC 2.0.

    Attributes:
        jsonrpc: versión del protocolo ("2.0").
        id: el mismo id de la solicitud.
        result: resultado en caso de éxito.
        error: JSONRPCError en caso de fallo.
    """
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None