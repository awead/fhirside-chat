from uuid import UUID
from fastapi.testclient import TestClient
from pydantic import BaseModel
import importlib

from src.models.clinical_history import PatientClinicalHistory  # isort: skip
app_module = importlib.import_module("src.app")  # get actual module not package attr

# Simple shim to monkeypatch patient_history_agent for tests
class DummyHistory(BaseModel):
    patient_id: UUID
    patient_name: str
    clinical_summary: str
    key_conditions: list[str] = []
    active_medications: list[str] = []
    recent_encounters: list[str] = []
    generated_at: str = "2025-11-14T00:00:00Z"

app = app_module.create_app()
client = TestClient(app)


def test_chat_endpoint_smoke():
    resp = client.post("/chat", json={"session_id": "t1", "message": "Hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"] == "t1"
    assert "output" in body


def test_patient_endpoint_422_invalid_uuid():
    resp = client.post("/patient", json={"patient_id": "bad-uuid"})
    assert resp.status_code == 422


def test_patient_endpoint_success(monkeypatch):
    class StubCtx:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def run(self, prompt: str):
            class R:
                def __init__(self):
                    self.data = PatientClinicalHistory(
                        patient_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                        patient_name="Jane Doe",
                        clinical_summary="Stable",
                    )
            return R()
    monkeypatch.setattr(app_module, "patient_history_agent", lambda: StubCtx())
    resp = client.post("/patient", json={"patient_id": "123e4567-e89b-12d3-a456-426614174000"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["patient_id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert body["clinical_summary"] == "Stable"


def test_patient_endpoint_404(monkeypatch):
    class StubCtx:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def run(self, prompt: str):
            class R:
                def __init__(self):
                    self.data = None
            return R()
    monkeypatch.setattr(app_module, "patient_history_agent", lambda: StubCtx())
    resp = client.post("/patient", json={"patient_id": "123e4567-e89b-12d3-a456-426614174000"})
    assert resp.status_code == 404


def test_patient_endpoint_500(monkeypatch):
    class StubCtx:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def run(self, prompt: str):
            raise RuntimeError("fail")
    monkeypatch.setattr(app_module, "patient_history_agent", lambda: StubCtx())
    resp = client.post("/patient", json={"patient_id": "123e4567-e89b-12d3-a456-426614174000"})
    assert resp.status_code == 500


def test_ws_chat_endpoint():
    with client.websocket_connect("/ws?session_id=ws1") as ws:
        ws.send_text("Hello via WS")
        reply = ws.receive_text()
        assert isinstance(reply, str)
        assert reply
