import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from src.models.telemetry import SpanData, SpanAttributes
from src.app import create_app


@pytest.fixture
def mock_spans():
    return [
        SpanData(
            span_id="span1",
            trace_id="trace1",
            operation_name="openai.chat.completion",
            start_time=1700000000000000000,
            end_time=1700000001000000000,
            duration=1000000000,
            attributes=SpanAttributes(
                **{
                    "openai.prompt": "test prompt",
                    "openai.model": "gpt-4o",
                    "session_id": "test-session",
                }
            ),
            status="OK",
        ),
        SpanData(
            span_id="span2",
            trace_id="trace1",
            operation_name="mcp.query",
            start_time=1700000001000000000,
            end_time=1700000002000000000,
            duration=1000000000,
            attributes=SpanAttributes(
                **{"mcp.query": "GET /Patient", "session_id": "test-session"}
            ),
            status="OK",
        ),
    ]


@patch("src.app.query_traces_by_session", new_callable=AsyncMock)
def test_telemetry_endpoint_success(mock_query, mock_spans):
    mock_query.return_value = mock_spans

    app = create_app()
    client = TestClient(app)

    response = client.get("/telemetry/test-session")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session"
    assert len(data["spans"]) == 2
    assert data["trace_count"] == 1
    assert data["spans"][0]["operation_name"] == "openai.chat.completion"
    assert data["spans"][1]["operation_name"] == "mcp.query"

    mock_query.assert_called_once_with("test-session")


@patch("src.app.query_traces_by_session", new_callable=AsyncMock)
def test_telemetry_endpoint_empty_response(mock_query):
    mock_query.return_value = []

    app = create_app()
    client = TestClient(app)

    response = client.get("/telemetry/empty-session")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "empty-session"
    assert data["spans"] == []
    assert data["trace_count"] == 0


@patch("src.app.query_traces_by_session", new_callable=AsyncMock)
def test_telemetry_endpoint_multiple_traces(mock_query):
    spans_with_multiple_traces = [
        SpanData(
            span_id="span1",
            trace_id="trace1",
            operation_name="openai.chat.completion",
            start_time=1700000000000000000,
            end_time=1700000001000000000,
            duration=1000000000,
            attributes=SpanAttributes(**{"session_id": "multi-trace"}),
            status="OK",
        ),
        SpanData(
            span_id="span2",
            trace_id="trace2",
            operation_name="openai.chat.completion",
            start_time=1700000002000000000,
            end_time=1700000003000000000,
            duration=1000000000,
            attributes=SpanAttributes(**{"session_id": "multi-trace"}),
            status="OK",
        ),
    ]

    mock_query.return_value = spans_with_multiple_traces

    app = create_app()
    client = TestClient(app)

    response = client.get("/telemetry/multi-trace")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "multi-trace"
    assert len(data["spans"]) == 2
    assert data["trace_count"] == 2


@patch("src.app.query_traces_by_session", new_callable=AsyncMock)
def test_telemetry_endpoint_error(mock_query):
    mock_query.side_effect = Exception("Jaeger error")

    app = create_app()
    client = TestClient(app)

    response = client.get("/telemetry/error-session")

    assert response.status_code == 500
    assert "Failed to retrieve telemetry data" in response.json()["detail"]
