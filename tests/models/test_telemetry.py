from src.models.telemetry import SpanAttributes, SpanData, TelemetryResponse


def test_span_attributes_with_openai_data():
    attrs = SpanAttributes(
        **{
            "openai.prompt": "test prompt",
            "openai.completion": "test response",
            "openai.model": "gpt-4o",
            "openai.token_count": 100,
            "session_id": "test-123",
        }
    )

    assert attrs.openai_prompt == "test prompt"
    assert attrs.openai_completion == "test response"
    assert attrs.openai_model == "gpt-4o"
    assert attrs.openai_token_count == 100
    assert attrs.session_id == "test-123"


def test_span_attributes_with_mcp_data():
    attrs = SpanAttributes(
        **{
            "mcp.query": "GET /Patient?count=true",
            "mcp.resource_type": "Patient",
            "mcp.response": '{"total": 42}',
            "session_id": "test-456",
        }
    )

    assert attrs.mcp_query == "GET /Patient?count=true"
    assert attrs.mcp_resource_type == "Patient"
    assert attrs.mcp_response == '{"total": 42}'
    assert attrs.session_id == "test-456"


def test_span_attributes_defaults_to_none():
    attrs = SpanAttributes()

    assert attrs.openai_prompt is None
    assert attrs.mcp_query is None
    assert attrs.session_id is None
    assert attrs.additional_attributes == {}


def test_span_data_serialization():
    span = SpanData(
        span_id="abc123",
        trace_id="xyz789",
        parent_span_id="parent456",
        operation_name="openai.chat.completion",
        start_time=1700000000000000000,
        end_time=1700000001000000000,
        duration=1000000000,
        attributes=SpanAttributes(session_id="test-session"),
        status="OK",
    )

    json_data = span.model_dump()

    assert json_data["span_id"] == "abc123"
    assert json_data["trace_id"] == "xyz789"
    assert json_data["operation_name"] == "openai.chat.completion"
    assert json_data["status"] == "OK"
    assert json_data["attributes"]["session_id"] == "test-session"


def test_span_data_with_error():
    span = SpanData(
        span_id="error123",
        trace_id="trace999",
        operation_name="mcp.query",
        start_time=1700000000000000000,
        end_time=1700000001000000000,
        duration=1000000000,
        attributes=SpanAttributes(),
        status="ERROR",
        error_message="Connection timeout",
    )

    assert span.status == "ERROR"
    assert span.error_message == "Connection timeout"


def test_telemetry_response_with_spans():
    response = TelemetryResponse(
        session_id="session-123",
        spans=[
            SpanData(
                span_id="span1",
                trace_id="trace1",
                operation_name="openai.chat.completion",
                start_time=1700000000000000000,
                end_time=1700000001000000000,
                duration=1000000000,
                attributes=SpanAttributes(session_id="session-123"),
                status="OK",
            ),
            SpanData(
                span_id="span2",
                trace_id="trace1",
                operation_name="mcp.query",
                start_time=1700000001000000000,
                end_time=1700000002000000000,
                duration=1000000000,
                attributes=SpanAttributes(session_id="session-123"),
                status="OK",
            ),
        ],
        trace_count=1,
    )

    assert response.session_id == "session-123"
    assert len(response.spans) == 2
    assert response.trace_count == 1


def test_telemetry_response_empty_spans():
    response = TelemetryResponse(session_id="empty-session", spans=[], trace_count=0)

    assert response.session_id == "empty-session"
    assert response.spans == []
    assert response.trace_count == 0


def test_telemetry_response_json_serialization():
    response = TelemetryResponse(
        session_id="json-test",
        spans=[
            SpanData(
                span_id="span-json",
                trace_id="trace-json",
                operation_name="openai.chat.completion",
                start_time=1700000000000000000,
                end_time=1700000001000000000,
                duration=1000000000,
                attributes=SpanAttributes(
                    **{"openai.prompt": "test", "session_id": "json-test"}
                ),
                status="OK",
            )
        ],
        trace_count=1,
    )

    json_data = response.model_dump()

    assert json_data["session_id"] == "json-test"
    assert len(json_data["spans"]) == 1
    assert json_data["spans"][0]["attributes"]["openai_prompt"] == "test"
    assert json_data["trace_count"] == 1
