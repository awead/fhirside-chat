from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
from pydantic_ai.models.instrumented import InstrumentationSettings

from src.ai.agents import chat_agent, patient_history_agent


def test_chat_agent(monkeypatch):
    monkeypatch.setenv("FHIR_CHAT_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("FHIR_CHAT_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("FHIR_CHAT_OPENAI_MODEL", "gpt-test")
    monkeypatch.setenv("FHIR_CHAT_OPENAI_API_VERSION", "2024-01-01")

    agent = chat_agent()

    assert isinstance(agent, Agent)
    assert agent.toolsets, "Agent should have at least one toolset"
    assert any(isinstance(ts, MCPServerSSE) for ts in agent.toolsets)
    assert isinstance(agent.instrument, InstrumentationSettings)


def test_patient_history_agent(monkeypatch):
    monkeypatch.setenv("FHIR_CHAT_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("FHIR_CHAT_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("FHIR_CHAT_OPENAI_MODEL", "gpt-test")
    monkeypatch.setenv("FHIR_CHAT_OPENAI_API_VERSION", "2024-01-01")

    agent = patient_history_agent()
    assert isinstance(agent, Agent)
    assert agent.output_type.__name__ == "PatientClinicalHistory"
    assert any(isinstance(ts, MCPServerSSE) for ts in agent.toolsets)
    assert isinstance(agent.instrument, InstrumentationSettings)
