"""Data models for OpenTelemetry trace data exposure."""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SpanAttributes(BaseModel):
    """OpenTelemetry span attributes containing operation-specific data."""

    openai_prompt: Optional[str] = Field(
        default=None, description="OpenAI prompt text", alias="openai.prompt"
    )
    openai_completion: Optional[str] = Field(
        default=None, description="OpenAI completion text", alias="openai.completion"
    )
    openai_model: Optional[str] = Field(
        default=None, description="OpenAI model name", alias="openai.model"
    )
    openai_token_count: Optional[int] = Field(
        default=None, description="OpenAI token count", alias="openai.token_count"
    )

    mcp_query: Optional[str] = Field(
        default=None, description="MCP FHIR query", alias="mcp.query"
    )
    mcp_resource_type: Optional[str] = Field(
        default=None,
        description="FHIR resource type queried",
        alias="mcp.resource_type",
    )
    mcp_response: Optional[str] = Field(
        default=None, description="MCP query response data", alias="mcp.response"
    )

    session_id: Optional[str] = Field(
        default=None, description="Session identifier for trace correlation"
    )

    additional_attributes: Dict[str, str] = Field(
        default_factory=dict, description="Other span attributes"
    )

    model_config = {"populate_by_name": True}


class SpanData(BaseModel):
    """OpenTelemetry span data."""

    span_id: str = Field(description="Unique span identifier")
    trace_id: str = Field(description="Trace identifier grouping related spans")
    parent_span_id: Optional[str] = Field(
        default=None, description="Parent span identifier for hierarchical tracing"
    )
    operation_name: str = Field(
        description="Operation name (e.g., 'openai.chat.completion', 'mcp.query')"
    )
    start_time: int = Field(
        description="Span start timestamp (nanoseconds since epoch)"
    )
    end_time: int = Field(description="Span end timestamp (nanoseconds since epoch)")
    duration: int = Field(description="Span duration in nanoseconds")
    attributes: SpanAttributes = Field(
        description="Span attributes containing operation-specific data"
    )
    status: str = Field(description="Span status: OK or ERROR")
    error_message: Optional[str] = Field(
        default=None, description="Error message if status is ERROR"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "span_id": "abc123",
                    "trace_id": "xyz789",
                    "parent_span_id": None,
                    "operation_name": "openai.chat.completion",
                    "start_time": 1700000000000000000,
                    "end_time": 1700000001000000000,
                    "duration": 1000000000,
                    "attributes": {
                        "openai.prompt": "What is the weather?",
                        "openai.completion": "I cannot access real-time weather data.",
                        "openai.model": "gpt-4o",
                        "openai.token_count": 150,
                        "session_id": "test-session-123",
                    },
                    "status": "OK",
                    "error_message": None,
                }
            ]
        }
    }


class TelemetryResponse(BaseModel):
    """Response model containing OpenTelemetry trace data for a session."""

    session_id: str = Field(description="Session identifier used to query traces")
    spans: List[SpanData] = Field(
        default_factory=list, description="List of spans associated with the session"
    )
    trace_count: int = Field(
        description="Total number of traces (unique trace_ids) in response"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "test-session-123",
                    "spans": [
                        {
                            "span_id": "abc123",
                            "trace_id": "xyz789",
                            "operation_name": "openai.chat.completion",
                            "start_time": 1700000000000000000,
                            "end_time": 1700000001000000000,
                            "duration": 1000000000,
                            "attributes": {
                                "openai.prompt": "How many patients?",
                                "openai.completion": "There are 42 patients.",
                                "session_id": "test-session-123",
                            },
                            "status": "OK",
                        }
                    ],
                    "trace_count": 1,
                }
            ]
        }
    }
