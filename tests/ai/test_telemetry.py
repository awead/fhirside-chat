from src.ai.telemetry import instrumentation


def test_instrumentation_settings():
    settings = instrumentation()

    assert settings.version == 2
    assert settings.include_content is True
    assert settings.tracer.resource.attributes.get("service.name") == "fhir-chat-agent"
