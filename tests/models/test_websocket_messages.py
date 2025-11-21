from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models.websocket_messages import (
    AssistantMessage,
    ConnectionStatus,
    ErrorMessage,
    OpenAIEvent,
    ToolCallEvent,
    ToolResultEvent,
    UserMessage,
)


def test_user_message_valid_data():
    msg = UserMessage(type="message", session_id="test-123", content="Hello WebSocket")
    assert msg.type == "message"
    assert msg.session_id == "test-123"
    assert msg.content == "Hello WebSocket"


def test_user_message_missing_required_field():
    with pytest.raises(ValidationError):
        UserMessage(type="message", session_id="test-123")


def test_user_message_json_serialization():
    msg = UserMessage(type="message", session_id="test-123", content="Hello WebSocket")
    json_str = msg.model_dump_json()
    assert "message" in json_str
    assert "test-123" in json_str
    assert "Hello WebSocket" in json_str


def test_assistant_message_with_defaults():
    msg = AssistantMessage(
        type="assistant", session_id="test-123", content="Response text"
    )
    assert msg.streaming is False


def test_assistant_message_with_streaming():
    msg = AssistantMessage(
        type="assistant", session_id="test-123", content="Streaming...", streaming=True
    )
    assert msg.streaming is True


def test_assistant_message_json_serialization():
    msg = AssistantMessage(
        type="assistant", session_id="test-123", content="Response text"
    )
    json_str = msg.model_dump_json()
    assert "assistant" in json_str
    assert "Response text" in json_str


def test_tool_call_event_all_fields():
    timestamp = datetime.now()
    event = ToolCallEvent(
        type="tool_call",
        session_id="test-123",
        tool_call_id="call-456",
        tool_name="fetch_patient_data",
        arguments={"patient_id": "quintin-cole"},
        timestamp=timestamp,
    )
    assert event.type == "tool_call"
    assert event.tool_call_id == "call-456"
    assert event.tool_name == "fetch_patient_data"
    assert event.arguments["patient_id"] == "quintin-cole"
    assert event.timestamp == timestamp


def test_tool_call_event_missing_required_field():
    with pytest.raises(ValidationError):
        ToolCallEvent(
            type="tool_call",
            session_id="test-123",
            tool_name="fetch_patient_data",
            arguments={},
        )


def test_tool_result_event_with_duration():
    timestamp = datetime.now()
    event = ToolResultEvent(
        type="tool_result",
        session_id="test-123",
        tool_call_id="call-456",
        tool_name="fetch_patient_data",
        result="Patient data retrieved",
        duration_ms=234,
        timestamp=timestamp,
    )
    assert event.duration_ms == 234
    assert event.result == "Patient data retrieved"


def test_tool_result_event_json_serialization():
    timestamp = datetime.now()
    event = ToolResultEvent(
        type="tool_result",
        session_id="test-123",
        tool_call_id="call-456",
        tool_name="fetch_patient_data",
        result="Success",
        duration_ms=100,
        timestamp=timestamp,
    )
    json_str = event.model_dump_json()
    assert "tool_result" in json_str
    assert "100" in json_str


def test_openai_event_call_type():
    timestamp = datetime.now()
    event = OpenAIEvent(
        type="openai_call", session_id="test-123", model="gpt-4", timestamp=timestamp
    )
    assert event.type == "openai_call"
    assert event.prompt_tokens is None
    assert event.completion_tokens is None


def test_openai_event_response_type_with_tokens():
    timestamp = datetime.now()
    event = OpenAIEvent(
        type="openai_response",
        session_id="test-123",
        model="gpt-4",
        prompt_tokens=150,
        completion_tokens=50,
        total_tokens=200,
        duration_ms=1234,
        timestamp=timestamp,
    )
    assert event.type == "openai_response"
    assert event.prompt_tokens == 150
    assert event.completion_tokens == 50
    assert event.total_tokens == 200
    assert event.duration_ms == 1234


def test_openai_event_optional_fields():
    timestamp = datetime.now()
    event = OpenAIEvent(
        type="openai_call", session_id="test-123", model="gpt-4", timestamp=timestamp
    )
    json_str = event.model_dump_json()
    assert "gpt-4" in json_str


def test_error_message_structure():
    msg = ErrorMessage(
        type="error", session_id="test-123", error="Invalid message format"
    )
    assert msg.type == "error"
    assert msg.error == "Invalid message format"


def test_error_message_json_serialization():
    msg = ErrorMessage(type="error", session_id="test-123", error="Validation failed")
    json_str = msg.model_dump_json()
    assert "error" in json_str
    assert "Validation failed" in json_str


def test_connection_status_connected():
    status = ConnectionStatus(
        type="connection", status="connected", session_id="test-123"
    )
    assert status.status == "connected"


def test_connection_status_disconnected():
    status = ConnectionStatus(
        type="connection", status="disconnected", session_id="test-123"
    )
    assert status.status == "disconnected"


def test_connection_status_reconnecting():
    status = ConnectionStatus(
        type="connection", status="reconnecting", session_id="test-123"
    )
    assert status.status == "reconnecting"


def test_connection_status_invalid_literal():
    with pytest.raises(ValidationError):
        ConnectionStatus(
            type="connection", status="invalid_status", session_id="test-123"
        )
