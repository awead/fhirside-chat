from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


class UserMessage(BaseModel):
    type: Literal["message"]
    session_id: str
    content: str


class AssistantMessage(BaseModel):
    type: Literal["assistant"]
    session_id: str
    content: str
    streaming: bool = False


class ToolCallEvent(BaseModel):
    type: Literal["tool_call"]
    session_id: str
    tool_call_id: str
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: datetime


class ToolResultEvent(BaseModel):
    type: Literal["tool_result"]
    session_id: str
    tool_call_id: str
    tool_name: str
    result: str
    duration_ms: int
    timestamp: datetime


class OpenAIEvent(BaseModel):
    type: Literal["openai_call", "openai_response"]
    session_id: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    duration_ms: Optional[int] = None
    timestamp: datetime


class ErrorMessage(BaseModel):
    type: Literal["error"]
    session_id: str
    error: str


class ConnectionStatus(BaseModel):
    type: Literal["connection"]
    status: Literal["connected", "disconnected", "reconnecting"]
    session_id: str
