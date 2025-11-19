import os

from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from src.ai.telemetry import instrumentation
from src.models.clinical_history import PatientClinicalHistory


api_key = os.getenv("FHIR_CHAT_OPENAI_API_KEY")
api_endpoint = os.getenv("FHIR_CHAT_OPENAI_ENDPOINT")
api_model = os.getenv("FHIR_CHAT_OPENAI_MODEL")
api_version = os.getenv("FHIR_CHAT_OPENAI_API_VERSION")


def chat_agent() -> Agent:
    mcp_server = MCPServerSSE("http://localhost:8080/sse")

    client = AsyncAzureOpenAI(
        azure_endpoint=api_endpoint,
        api_version=api_version,
        api_key=api_key,
    )

    model = OpenAIChatModel(api_model, provider=OpenAIProvider(openai_client=client))
    agent = Agent(model, toolsets=[mcp_server], instrument=instrumentation())
    return agent


def patient_history_agent() -> Agent[PatientClinicalHistory]:
    """Agent configured to generate a patient clinical history.

    Uses the MCP FHIR server to gather patient-related resources and synthesizes
    a structured clinical history output.
    """
    mcp_server = MCPServerSSE("http://localhost:8080/sse")
    client = AsyncAzureOpenAI(
        azure_endpoint=api_endpoint,
        api_version=api_version,
        api_key=api_key,
    )
    system_prompt = (
        "You are a clinical summarization assistant. Given a patient UUID, "
        "query the FHIR server for Patient, Condition, MedicationRequest, and Encounter resources. "
        "Construct a concise narrative (clinical_summary) and populate lists of key conditions, "
        "active medications, and recent encounters (date: type or reason). If data is missing, "
        "leave lists empty. Return ONLY valid structured data without prose outside fields."
    )
    model = OpenAIChatModel(api_model, provider=OpenAIProvider(openai_client=client))
    agent = Agent(
        model,
        toolsets=[mcp_server],
        instrument=instrumentation(),
        system_prompt=system_prompt,
        output_type=PatientClinicalHistory
    )
    return agent
