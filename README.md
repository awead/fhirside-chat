# FHIRside Chat

A structured Python application using PydanticAI with an Aidbox FHIR MCP Server.

## Configuration

You will need:

* Aidbox license
* OpenAI access
    - endpoint
    - key
    - model (currently testing with gpt-5-mini)
    - API version (currently testing with 2024-12-01-preview)

See `env-sample.txt`

## Usage

Start services:

```bash
docker compose up -d
```

Start the API backend:

```bash
uv run uvicorn src:app --host 0.0.0.0 --port 8000 --reload
```

Send a test chat message:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"abc","message":"How many patients are in the system?"}'
```

For telemetry information, visit [Jaeger](http://localhost:16686).

## Notes
* In-memory sessions only; replace `ChatService` for persistence.
* Ensure Aidbox healthcheck passes; SSE endpoint is `http://localhost:8080/sse`.
