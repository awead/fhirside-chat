from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.telemetry.event_emitter import TelemetryEmitter


@pytest.mark.asyncio
async def test_emit_tool_call_sends_event():
    mock_connection_manager = AsyncMock()
    emitter = TelemetryEmitter(mock_connection_manager)

    await emitter.emit_tool_call(
        session_id="test-session",
        tool_call_id="call-123",
        tool_name="fetch_patient_data",
        arguments={"patient_id": "quintin-cole"},
    )

    mock_connection_manager.send_message.assert_called_once()
    call_args = mock_connection_manager.send_message.call_args
    assert call_args[0][0] == "test-session"

    event = call_args[0][1]
    assert event.type == "tool_call"
    assert event.session_id == "test-session"
    assert event.tool_call_id == "call-123"
    assert event.tool_name == "fetch_patient_data"
    assert event.arguments == {"patient_id": "quintin-cole"}
    assert isinstance(event.timestamp, datetime)


@pytest.mark.asyncio
async def test_emit_tool_result_includes_duration():
    mock_connection_manager = AsyncMock()
    emitter = TelemetryEmitter(mock_connection_manager)

    await emitter.emit_tool_result(
        session_id="test-session",
        tool_call_id="call-123",
        tool_name="fetch_patient_data",
        result="Patient data retrieved successfully",
        duration_ms=234,
    )

    mock_connection_manager.send_message.assert_called_once()
    call_args = mock_connection_manager.send_message.call_args
    event = call_args[0][1]

    assert event.type == "tool_result"
    assert event.tool_call_id == "call-123"
    assert event.result == "Patient data retrieved successfully"
    assert event.duration_ms == 234
    assert isinstance(event.timestamp, datetime)


@pytest.mark.asyncio
async def test_emit_openai_call_with_event_type():
    mock_connection_manager = AsyncMock()
    emitter = TelemetryEmitter(mock_connection_manager)

    await emitter.emit_openai_call(
        session_id="test-session",
        event_type="openai_call",
        model="gpt-4",
    )

    mock_connection_manager.send_message.assert_called_once()
    call_args = mock_connection_manager.send_message.call_args
    event = call_args[0][1]

    assert event.type == "openai_call"
    assert event.model == "gpt-4"
    assert event.prompt_tokens is None
    assert event.completion_tokens is None
    assert isinstance(event.timestamp, datetime)


@pytest.mark.asyncio
async def test_emit_openai_response_with_tokens():
    mock_connection_manager = AsyncMock()
    emitter = TelemetryEmitter(mock_connection_manager)

    await emitter.emit_openai_call(
        session_id="test-session",
        event_type="openai_response",
        model="gpt-4",
        prompt_tokens=150,
        completion_tokens=50,
        total_tokens=200,
        duration_ms=1234,
    )

    mock_connection_manager.send_message.assert_called_once()
    call_args = mock_connection_manager.send_message.call_args
    event = call_args[0][1]

    assert event.type == "openai_response"
    assert event.model == "gpt-4"
    assert event.prompt_tokens == 150
    assert event.completion_tokens == 50
    assert event.total_tokens == 200
    assert event.duration_ms == 1234


@pytest.mark.asyncio
async def test_emit_tool_call_handles_connection_error():
    mock_connection_manager = AsyncMock()
    mock_connection_manager.send_message.side_effect = Exception("Connection lost")
    emitter = TelemetryEmitter(mock_connection_manager)

    await emitter.emit_tool_call(
        session_id="test-session",
        tool_call_id="call-123",
        tool_name="fetch_patient_data",
        arguments={},
    )


@pytest.mark.asyncio
async def test_emit_tool_result_handles_connection_error():
    mock_connection_manager = AsyncMock()
    mock_connection_manager.send_message.side_effect = Exception("Connection lost")
    emitter = TelemetryEmitter(mock_connection_manager)

    await emitter.emit_tool_result(
        session_id="test-session",
        tool_call_id="call-123",
        tool_name="fetch_patient_data",
        result="Success",
        duration_ms=100,
    )


@pytest.mark.asyncio
async def test_emit_openai_call_handles_connection_error():
    mock_connection_manager = AsyncMock()
    mock_connection_manager.send_message.side_effect = Exception("Connection lost")
    emitter = TelemetryEmitter(mock_connection_manager)

    await emitter.emit_openai_call(
        session_id="test-session",
        event_type="openai_call",
        model="gpt-4",
    )


@pytest.mark.asyncio
async def test_emit_methods_are_fire_and_forget():
    mock_connection_manager = AsyncMock()
    emitter = TelemetryEmitter(mock_connection_manager)

    await emitter.emit_tool_call(
        session_id="test-session",
        tool_call_id="call-123",
        tool_name="test_tool",
        arguments={},
    )

    await emitter.emit_tool_result(
        session_id="test-session",
        tool_call_id="call-123",
        tool_name="test_tool",
        result="Done",
        duration_ms=50,
    )

    await emitter.emit_openai_call(
        session_id="test-session",
        event_type="openai_call",
        model="gpt-4",
    )

    assert mock_connection_manager.send_message.call_count == 3
