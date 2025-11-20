"""Jaeger Query API client for retrieving OpenTelemetry trace data."""

from typing import List
import logging

import httpx

from src.models.telemetry import SpanData, SpanAttributes


logger = logging.getLogger(__name__)

JAEGER_QUERY_URL = "http://localhost:16686/api/traces"
JAEGER_TIMEOUT = 5.0
SERVICE_NAME = "fhir-chat-agent"


async def query_traces_by_session(session_id: str) -> List[SpanData]:
    """Query Jaeger for traces associated with a session ID.

    Args:
        session_id: Session identifier to filter traces.

    Returns:
        List of SpanData objects containing trace information.
        Returns empty list if Jaeger is unavailable or no traces found.
    """
    try:
        async with httpx.AsyncClient(timeout=JAEGER_TIMEOUT) as client:
            response = await client.get(
                JAEGER_QUERY_URL,
                params={
                    "service": SERVICE_NAME,
                    "tag": f"session_id:{session_id}",
                    "limit": 100,
                },
            )
            response.raise_for_status()

            jaeger_data = response.json()
            spans = _parse_jaeger_response(jaeger_data, session_id)

            logger.info(
                "jaeger_query_success",
                extra={"session_id": session_id, "span_count": len(spans)},
            )
            return spans

    except httpx.TimeoutException:
        logger.error(
            "jaeger_query_timeout",
            extra={"session_id": session_id, "timeout": JAEGER_TIMEOUT},
        )
        return []
    except httpx.HTTPError as e:
        logger.error(
            "jaeger_query_http_error", extra={"session_id": session_id, "error": str(e)}
        )
        return []
    except Exception as e:
        logger.error(
            "jaeger_query_error", extra={"session_id": session_id, "error": str(e)}
        )
        return []


def _parse_jaeger_response(jaeger_data: dict, session_id: str) -> List[SpanData]:
    """Parse Jaeger JSON response into SpanData objects.

    Args:
        jaeger_data: Raw JSON response from Jaeger Query API.
        session_id: Session ID for context.

    Returns:
        List of parsed SpanData objects.
    """
    spans = []

    jaeger_traces = jaeger_data.get("data", [])

    for trace in jaeger_traces:
        for jaeger_span in trace.get("spans", []):
            if _is_relevant_span(jaeger_span):
                try:
                    span_data = _convert_jaeger_span(jaeger_span)
                    spans.append(span_data)
                except Exception as e:
                    logger.warning(
                        "span_parsing_error",
                        extra={
                            "session_id": session_id,
                            "span_id": jaeger_span.get("spanID"),
                            "error": str(e),
                        },
                    )

    return spans


def _is_relevant_span(jaeger_span: dict) -> bool:
    """Check if span is relevant (OpenAI, MCP, or agent operation).

    Args:
        jaeger_span: Jaeger span object.

    Returns:
        True if span should be included in results.
    """
    operation_name = jaeger_span.get("operationName", "")

    return (
        operation_name.startswith("openai.")
        or operation_name.startswith("mcp.")
        or operation_name.startswith("chat ")
        or operation_name.startswith("agent ")
        or "OpenAI" in operation_name
        or "MCP" in operation_name
        or "Aidbox" in operation_name
        or "gpt" in operation_name.lower()
        or operation_name == "chat_session"
        or operation_name == "running tool"
        or operation_name == "running tools"
    )


def _convert_jaeger_span(jaeger_span: dict) -> SpanData:
    """Convert Jaeger span format to SpanData model.

    Args:
        jaeger_span: Jaeger span object.

    Returns:
        SpanData model instance.
    """
    span_id = jaeger_span.get("spanID", "")
    trace_id = jaeger_span.get("traceID", "")
    operation_name = jaeger_span.get("operationName", "")
    start_time = jaeger_span.get("startTime", 0)
    duration = jaeger_span.get("duration", 0)
    end_time = start_time + duration

    references = jaeger_span.get("references", [])
    parent_span_id = None
    for ref in references:
        if ref.get("refType") == "CHILD_OF":
            parent_span_id = ref.get("spanID")
            break

    tags = jaeger_span.get("tags", [])
    attributes_dict = {tag["key"]: tag.get("value", "") for tag in tags}

    attributes = SpanAttributes(**attributes_dict)

    status = "OK"
    error_message = None

    status_tag = next((tag for tag in tags if tag["key"] == "otel.status_code"), None)
    if status_tag and status_tag.get("value") == "ERROR":
        status = "ERROR"
        error_tag = next((tag for tag in tags if tag["key"] == "error.message"), None)
        if error_tag:
            error_message = error_tag.get("value")

    return SpanData(
        span_id=span_id,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
        operation_name=operation_name,
        start_time=start_time,
        end_time=end_time,
        duration=duration,
        attributes=attributes,
        status=status,
        error_message=error_message,
    )
