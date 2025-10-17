import os

from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from src.ai.telemetry import instrumentation


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
