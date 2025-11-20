import logging
from typing import Dict

from fastapi import WebSocket
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("websocket_connected", extra={"session_id": session_id})

    async def disconnect(self, session_id: str) -> None:
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info("websocket_disconnected", extra={"session_id": session_id})

    async def send_message(self, session_id: str, message: BaseModel) -> None:
        websocket = self.active_connections.get(session_id)
        if websocket is None:
            logger.warning(
                "websocket_send_failed_no_connection", extra={"session_id": session_id}
            )
            return

        try:
            json_message = message.model_dump_json()
            await websocket.send_text(json_message)
        except Exception as e:
            logger.error(
                "websocket_send_failed",
                extra={"session_id": session_id, "error": str(e)},
            )
