import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from opentelemetry import trace
from pydantic import BaseModel
from typing import Dict, List

from src.models.clinical_history import (
    PatientHistoryRequest,
    PatientClinicalHistory,
)
from src.models.telemetry import TelemetryResponse
from src.telemetry.jaeger_client import query_traces_by_session

from .ai.agents import chat_agent, patient_history_agent


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    output: str


class ChatService:
    """Manages simple in-memory chat sessions and delegates to the agent."""

    def __init__(self) -> None:
        self._sessions: Dict[str, List[str]] = {}

    async def process(self, session_id: str, message: str) -> str:
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute("session_id", session_id)

        history = self._sessions.setdefault(session_id, [])
        history.append(f"User: {message}")
        prompt = "\n".join(history) + "\nAssistant:"

        try:
            async with chat_agent() as agent:
                result = await agent.run(prompt)
                output = result.output
        except Exception as e:  # probably shouldn't do this
            output = f"Error: {e}"

        history.append(f"Assistant: {output}")
        return output


chat_service = ChatService()


def create_app() -> FastAPI:
    app = FastAPI(title="FHIR Chat Agent")
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("patient_history")
    telemetry_logger = logging.getLogger("telemetry")

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):  # noqa: D401 - FastAPI handler
        output = await chat_service.process(req.session_id, req.message)
        return ChatResponse(session_id=req.session_id, output=output)

    @app.websocket("/ws")
    async def ws_chat(websocket: WebSocket):
        await websocket.accept()
        session_id = websocket.query_params.get("session_id", "default")
        try:
            while True:
                msg = await websocket.receive_text()
                output = await chat_service.process(session_id, msg)
                await websocket.send_text(output)
        except WebSocketDisconnect:
            return

    @app.post("/patient", response_model=PatientClinicalHistory)
    async def patient_history(req: PatientHistoryRequest):
        """Generate clinical history for a patient.

        Returns structured clinical data synthesized from FHIR resources.
        Raises:
            HTTPException: 404 if patient not found, 500 for internal failures.
        """
        # Build a minimal prompt; agent system prompt guides data gathering.
        prompt = f"patient_id: {req.patient_id}"
        try:
            async with patient_history_agent() as agent:
                result = await agent.run(prompt)
                history = result.output
        except Exception as e:  # broad catch; refine if needed
            logger.exception(
                "patient_history_error", extra={"patient_id": str(req.patient_id)}
            )
            raise HTTPException(
                status_code=500, detail="Internal error generating patient history"
            ) from e
        if not history:
            logger.info(
                "patient_history_not_found", extra={"patient_id": str(req.patient_id)}
            )
            raise HTTPException(status_code=404, detail="Patient not found or no data")
        logger.info(
            "patient_history_success", extra={"patient_id": str(req.patient_id)}
        )
        return history

    @app.get("/telemetry/{session_id}", response_model=TelemetryResponse)
    async def get_telemetry(session_id: str):
        """Retrieve OpenTelemetry trace data for a session.

        Returns trace spans for OpenAI and MCP operations associated with the session.
        Returns empty list if no traces found or Jaeger unavailable.

        Raises:
            HTTPException: 500 for internal failures.
        """
        telemetry_logger.info("telemetry_query", extra={"session_id": session_id})

        try:
            spans = await query_traces_by_session(session_id)

            unique_trace_ids = set(span.trace_id for span in spans)
            trace_count = len(unique_trace_ids)

            telemetry_logger.info(
                "telemetry_query_success",
                extra={
                    "session_id": session_id,
                    "span_count": len(spans),
                    "trace_count": trace_count,
                },
            )

            return TelemetryResponse(
                session_id=session_id, spans=spans, trace_count=trace_count
            )

        except Exception as e:
            telemetry_logger.error(
                "telemetry_query_error",
                extra={"session_id": session_id, "error": str(e)},
            )
            raise HTTPException(
                status_code=500, detail="Failed to retrieve telemetry data"
            ) from e

    return app


app = create_app()
