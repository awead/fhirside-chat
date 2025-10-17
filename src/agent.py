import os
from typing import Any

from openai import AsyncAzureOpenAI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
from pydantic_ai.models.instrumented import InstrumentationSettings
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .models.patient import PatientBase


class FhirChatAgent:
    """Encapsulates configuration and execution of the PydanticAI FHIR chat agent."""

    def __init__(
        self,
        *,
        sse_endpoint: str | None = None,
    ) -> None:
        resource = Resource.create({"service.name": "fhir-chat-agent"})
        tracer_provider = TracerProvider(resource=resource)
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://localhost:4317", insecure=True
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        trace.set_tracer_provider(tracer_provider)

        self._server = MCPServerSSE(sse_endpoint or "http://localhost:8080/sse")

        api_key = os.getenv("FHIR_CHAT_OPENAI_API_KEY")
        api_endpoint = os.getenv("FHIR_CHAT_OPENAI_ENDPOINT")
        api_model = os.getenv("FHIR_CHAT_OPENAI_MODEL")
        api_version = os.getenv("FHIR_CHAT_OPENAI_API_VERSION")

        client = AsyncAzureOpenAI(
            azure_endpoint=api_endpoint,
            api_version=api_version,
            api_key=api_key,
        )
        model = OpenAIChatModel(
            api_model, provider=OpenAIProvider(openai_client=client)
        )

        instrumentation = InstrumentationSettings(
            tracer_provider=tracer_provider,
            include_content=True,
            version=2,
        )
        self._agent = Agent(
            model,
            toolsets=[self._server],
            instrument=instrumentation,
            output_type=PatientBase,
        )

    @property
    def agent(self) -> Agent:
        return self._agent

    async def run(self, prompt: str) -> Any:
        async with self._agent:
            result = await self._agent.run(prompt)
        return result.output


fhir_chat_agent = FhirChatAgent()
