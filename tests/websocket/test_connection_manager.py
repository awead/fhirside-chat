from unittest.mock import AsyncMock

import pytest

from src.models.websocket_messages import AssistantMessage, ErrorMessage
from src.websocket.connection_manager import ConnectionManager


@pytest.mark.asyncio
async def test_connect_adds_connection_to_mapping():
    manager = ConnectionManager()
    mock_websocket = AsyncMock()
    session_id = "test-session-123"

    await manager.connect(mock_websocket, session_id)

    assert session_id in manager.active_connections
    assert manager.active_connections[session_id] == mock_websocket
    mock_websocket.accept.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_removes_connection_from_mapping():
    manager = ConnectionManager()
    mock_websocket = AsyncMock()
    session_id = "test-session-123"

    await manager.connect(mock_websocket, session_id)
    await manager.disconnect(session_id)

    assert session_id not in manager.active_connections


@pytest.mark.asyncio
async def test_disconnect_with_nonexistent_session():
    manager = ConnectionManager()

    await manager.disconnect("nonexistent-session")

    assert len(manager.active_connections) == 0


@pytest.mark.asyncio
async def test_send_message_sends_json_to_correct_session():
    manager = ConnectionManager()
    mock_websocket = AsyncMock()
    session_id = "test-session-123"

    await manager.connect(mock_websocket, session_id)

    message = AssistantMessage(
        type="assistant", session_id=session_id, content="Test response"
    )
    await manager.send_message(session_id, message)

    mock_websocket.send_text.assert_called_once()
    sent_json = mock_websocket.send_text.call_args[0][0]
    assert "assistant" in sent_json
    assert "Test response" in sent_json


@pytest.mark.asyncio
async def test_send_message_handles_missing_session_gracefully():
    manager = ConnectionManager()
    message = AssistantMessage(
        type="assistant", session_id="missing-session", content="Test"
    )

    await manager.send_message("missing-session", message)


@pytest.mark.asyncio
async def test_send_message_handles_websocket_send_error():
    manager = ConnectionManager()
    mock_websocket = AsyncMock()
    mock_websocket.send_text.side_effect = Exception("Connection lost")
    session_id = "test-session-123"

    await manager.connect(mock_websocket, session_id)

    message = AssistantMessage(type="assistant", session_id=session_id, content="Test")
    await manager.send_message(session_id, message)


@pytest.mark.asyncio
async def test_multiple_concurrent_connections():
    manager = ConnectionManager()
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    mock_ws3 = AsyncMock()

    await manager.connect(mock_ws1, "session-1")
    await manager.connect(mock_ws2, "session-2")
    await manager.connect(mock_ws3, "session-3")

    assert len(manager.active_connections) == 3
    assert manager.active_connections["session-1"] == mock_ws1
    assert manager.active_connections["session-2"] == mock_ws2
    assert manager.active_connections["session-3"] == mock_ws3


@pytest.mark.asyncio
async def test_session_isolation_messages_only_to_intended_session():
    manager = ConnectionManager()
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()

    await manager.connect(mock_ws1, "session-1")
    await manager.connect(mock_ws2, "session-2")

    message = AssistantMessage(
        type="assistant", session_id="session-1", content="Message for session 1"
    )
    await manager.send_message("session-1", message)

    mock_ws1.send_text.assert_called_once()
    mock_ws2.send_text.assert_not_called()


@pytest.mark.asyncio
async def test_connection_manager_handles_error_message_type():
    manager = ConnectionManager()
    mock_websocket = AsyncMock()
    session_id = "test-session"

    await manager.connect(mock_websocket, session_id)

    error_msg = ErrorMessage(
        type="error", session_id=session_id, error="Validation failed"
    )
    await manager.send_message(session_id, error_msg)

    mock_websocket.send_text.assert_called_once()
    sent_json = mock_websocket.send_text.call_args[0][0]
    assert "error" in sent_json
    assert "Validation failed" in sent_json
