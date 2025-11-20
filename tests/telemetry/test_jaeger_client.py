import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from src.telemetry.jaeger_client import (
    query_traces_by_session,
    _parse_jaeger_response,
    _is_relevant_span,
    _convert_jaeger_span,
)


@pytest.fixture
def mock_jaeger_response():
    return {
        "data": [
            {
                "traceID": "trace123",
                "spans": [
                    {
                        "spanID": "span1",
                        "traceID": "trace123",
                        "operationName": "openai.chat.completion",
                        "startTime": 1700000000000000,
                        "duration": 1000000000,
                        "tags": [
                            {"key": "openai.prompt", "value": "test prompt"},
                            {"key": "openai.model", "value": "gpt-4o"},
                            {"key": "session_id", "value": "test-session"},
                            {"key": "otel.status_code", "value": "OK"},
                        ],
                        "references": [],
                    },
                    {
                        "spanID": "span2",
                        "traceID": "trace123",
                        "operationName": "mcp.query",
                        "startTime": 1700000001000000,
                        "duration": 500000000,
                        "tags": [
                            {"key": "mcp.query", "value": "GET /Patient"},
                            {"key": "mcp.resource_type", "value": "Patient"},
                            {"key": "session_id", "value": "test-session"},
                        ],
                        "references": [{"refType": "CHILD_OF", "spanID": "span1"}],
                    },
                    {
                        "spanID": "span3",
                        "traceID": "trace123",
                        "operationName": "internal.function",
                        "startTime": 1700000002000000,
                        "duration": 100000000,
                        "tags": [],
                        "references": [],
                    },
                ],
            }
        ]
    }


@pytest.mark.asyncio
async def test_query_traces_by_session_success(mock_jaeger_response):
    mock_response = Mock()
    mock_response.json.return_value = mock_jaeger_response
    mock_response.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client

        spans = await query_traces_by_session("test-session")

        assert len(spans) == 2
        assert spans[0].operation_name == "openai.chat.completion"
        assert spans[1].operation_name == "mcp.query"

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args.kwargs["params"]["service"] == "fhir-chat-agent"
        assert call_args.kwargs["params"]["tag"] == "session_id:test-session"


@pytest.mark.asyncio
async def test_query_traces_by_session_timeout():
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("Timeout")

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client

        spans = await query_traces_by_session("test-session")

        assert spans == []


@pytest.mark.asyncio
async def test_query_traces_by_session_http_error():
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.HTTPError("HTTP Error")

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client

        spans = await query_traces_by_session("test-session")

        assert spans == []


@pytest.mark.asyncio
async def test_query_traces_by_session_empty_response():
    mock_response = Mock()
    mock_response.json.return_value = {"data": []}
    mock_response.raise_for_status = Mock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client

        spans = await query_traces_by_session("empty-session")

        assert spans == []


def test_parse_jaeger_response(mock_jaeger_response):
    spans = _parse_jaeger_response(mock_jaeger_response, "test-session")

    assert len(spans) == 2
    assert spans[0].span_id == "span1"
    assert spans[0].trace_id == "trace123"
    assert spans[1].span_id == "span2"
    assert spans[1].parent_span_id == "span1"


def test_is_relevant_span_openai():
    span = {"operationName": "openai.chat.completion"}
    assert _is_relevant_span(span) is True


def test_is_relevant_span_mcp():
    span = {"operationName": "mcp.query"}
    assert _is_relevant_span(span) is True


def test_is_relevant_span_aidbox():
    span = {"operationName": "Aidbox.query"}
    assert _is_relevant_span(span) is True


def test_is_relevant_span_irrelevant():
    span = {"operationName": "internal.function"}
    assert _is_relevant_span(span) is False


def test_convert_jaeger_span_with_openai_attributes():
    jaeger_span = {
        "spanID": "test-span",
        "traceID": "test-trace",
        "operationName": "openai.chat.completion",
        "startTime": 1700000000000000,
        "duration": 1000000000,
        "tags": [
            {"key": "openai.prompt", "value": "test prompt"},
            {"key": "openai.model", "value": "gpt-4o"},
            {"key": "openai.token_count", "value": 150},
            {"key": "session_id", "value": "test-123"},
        ],
        "references": [],
    }

    span_data = _convert_jaeger_span(jaeger_span)

    assert span_data.span_id == "test-span"
    assert span_data.trace_id == "test-trace"
    assert span_data.operation_name == "openai.chat.completion"
    assert span_data.attributes.openai_prompt == "test prompt"
    assert span_data.attributes.openai_model == "gpt-4o"
    assert span_data.attributes.openai_token_count == 150
    assert span_data.status == "OK"


def test_convert_jaeger_span_with_error():
    jaeger_span = {
        "spanID": "error-span",
        "traceID": "error-trace",
        "operationName": "mcp.query",
        "startTime": 1700000000000000,
        "duration": 1000000000,
        "tags": [
            {"key": "otel.status_code", "value": "ERROR"},
            {"key": "error.message", "value": "Connection failed"},
        ],
        "references": [],
    }

    span_data = _convert_jaeger_span(jaeger_span)

    assert span_data.status == "ERROR"
    assert span_data.error_message == "Connection failed"


def test_convert_jaeger_span_with_parent_reference():
    jaeger_span = {
        "spanID": "child-span",
        "traceID": "test-trace",
        "operationName": "mcp.query",
        "startTime": 1700000000000000,
        "duration": 1000000000,
        "tags": [],
        "references": [{"refType": "CHILD_OF", "spanID": "parent-span"}],
    }

    span_data = _convert_jaeger_span(jaeger_span)

    assert span_data.parent_span_id == "parent-span"
