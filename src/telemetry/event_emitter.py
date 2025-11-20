import logging
from datetime import datetime
from typing import Any, Dict, Optional

from src.models.websocket_messages import OpenAIEvent, ToolCallEvent, ToolResultEvent
from src.websocket.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class TelemetryEmitter:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    async def emit_tool_call(
        self,
        session_id: str,
        tool_call_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> None:
        try:
            event = ToolCallEvent(
                type="tool_call",
                session_id=session_id,
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                arguments=arguments,
                timestamp=datetime.now(),
            )
            await self.connection_manager.send_message(session_id, event)
        except Exception as e:
            logger.warning(
                "telemetry_emit_tool_call_failed",
                extra={"session_id": session_id, "error": str(e)},
            )

    async def emit_tool_result(
        self,
        session_id: str,
        tool_call_id: str,
        tool_name: str,
        result: str,
        duration_ms: int,
    ) -> None:
        try:
            event = ToolResultEvent(
                type="tool_result",
                session_id=session_id,
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                result=result,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
            )
            await self.connection_manager.send_message(session_id, event)
        except Exception as e:
            logger.warning(
                "telemetry_emit_tool_result_failed",
                extra={"session_id": session_id, "error": str(e)},
            )

    async def emit_openai_call(
        self,
        session_id: str,
        event_type: str,
        model: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        try:
            event = OpenAIEvent(
                type=event_type,
                session_id=session_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
            )
            await self.connection_manager.send_message(session_id, event)
        except Exception as e:
            logger.warning(
                "telemetry_emit_openai_call_failed",
                extra={"session_id": session_id, "error": str(e)},
            )
