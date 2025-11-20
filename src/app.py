import json
import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from pydantic import BaseModel, ValidationError
from typing import Dict, List

from src.models.clinical_history import (
    PatientHistoryRequest,
    PatientClinicalHistory,
)
from src.models.telemetry import TelemetryResponse
from src.models.websocket_messages import (
    AssistantMessage,
    ErrorMessage,
    UserMessage,
)
from src.telemetry.jaeger_client import query_traces_by_session
from src.ai.telemetry import instrumentation
from src.websocket.connection_manager import ConnectionManager

from .ai.agents import chat_agent, patient_history_agent

instrumentation()


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
        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span(
            "chat_session", attributes={"session_id": session_id}
        ):
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
connection_manager = ConnectionManager()


def create_app() -> FastAPI:
    app = FastAPI(title="FHIR Chat Agent")
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("patient_history")
    telemetry_logger = logging.getLogger("telemetry")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):  # noqa: D401 - FastAPI handler
        output = await chat_service.process(req.session_id, req.message)
        return ChatResponse(session_id=req.session_id, output=output)

    @app.websocket("/ws")
    async def ws_chat(websocket: WebSocket):
        session_id = websocket.query_params.get("session_id", "default")
        await connection_manager.connect(websocket, session_id)

        try:
            while True:
                raw_message = await websocket.receive_text()

                try:
                    message_data = json.loads(raw_message)
                    user_message = UserMessage(**message_data)

                    if user_message.type == "message":
                        output = await chat_service.process(
                            user_message.session_id, user_message.content
                        )
                        response = AssistantMessage(
                            type="assistant",
                            session_id=user_message.session_id,
                            content=output,
                            streaming=False,
                        )
                        await connection_manager.send_message(
                            user_message.session_id, response
                        )

                except (json.JSONDecodeError, ValidationError) as e:
                    error_response = ErrorMessage(
                        type="error",
                        session_id=session_id,
                        error=f"Invalid message format: {str(e)}",
                    )
                    await connection_manager.send_message(session_id, error_response)

        except WebSocketDisconnect:
            await connection_manager.disconnect(session_id)

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

    frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
    if frontend_dist.exists() and frontend_dist.is_dir():
        app.mount(
            "/",
            StaticFiles(directory=str(frontend_dist), html=True),
            name="frontend",
        )

    return app


app = create_app()
FastAPIInstrumentor.instrument_app(app)
