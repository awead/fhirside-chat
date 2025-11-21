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

### Prerequisites

- **Backend:** Python 3.13+, `uv` package manager
- **Frontend:** Node.js 18+ and npm
- **Services:** Docker and Docker Compose

### Quick Start

1. **Start services:**

```bash
docker compose up -d
```

2. **Start the API backend:**

```bash
uv run uvicorn src:app --host 0.0.0.0 --port 8000 --reload
```

3. **Start the frontend (in a new terminal):**

```bash
cd frontend
npm install  # First time only
npm run dev
```

4. **Open the chat interface:**

Visit http://localhost:5173 in your browser

### Frontend Development

The frontend is a React + TypeScript application built with Vite.

**Available scripts:**
- `npm run dev` - Start development server (http://localhost:5173)
- `npm run build` - Build for production (outputs to `frontend/dist/`)
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

**Features:**
- Real-time WebSocket chat communication
- Session management with localStorage persistence
- Auto-scroll chat interface
- Streaming message support with typewriter effect
- Real-time telemetry panel showing OpenAI and MCP/Aidbox traces (<100ms latency)
- Connection status indicator with auto-reconnection
- Loading states and error handling

**Troubleshooting:**
- **CORS errors:** Ensure backend is running and CORS is configured for localhost:5173
- **Backend connection failed:** Check that the backend is running on port 8000
- **Port 5173 in use:** Vite will auto-increment to 5174, or use `npm run dev -- --port 3000`

### Production Build

To build and serve the frontend from the FastAPI backend:

1. **Build the frontend:**

```bash
cd frontend
npm run build
```

This creates optimized static files in `frontend/dist/`.

2. **Start the backend:**

```bash
uv run uvicorn src:app --host 0.0.0.0 --port 8000
```

3. **Access the application:**

Visit http://localhost:8000 in your browser. The backend automatically serves the frontend if `frontend/dist/` exists.

**Notes:**
- API routes (`/ws`, `/patient`) take precedence over static files
- The frontend uses client-side routing with SPA fallback
- Bundle sizes: CSS ~12KB, JS ~250KB (gzipped: ~3KB CSS, ~79KB JS)

### WebSocket API

The chat interface uses WebSocket for real-time bidirectional communication.

**Connection URL:**
```
ws://localhost:8000/ws?session_id=<your-session-id>
```

**Message Format:**

All messages are JSON with a `type` field for routing.

**Client → Server (UserMessage):**
```json
{
  "type": "message",
  "session_id": "your-session-id",
  "content": "What is quintin cole's diagnosis?"
}
```

**Server → Client:**

*Assistant Response:*
```json
{
  "type": "assistant",
  "session_id": "your-session-id",
  "content": "Based on the clinical data...",
  "streaming": false
}
```

*OpenAI Call Event:*
```json
{
  "type": "openai_call",
  "session_id": "your-session-id",
  "model": "gpt-4",
  "timestamp": "2025-11-20T22:00:00Z"
}
```

*OpenAI Response Event:*
```json
{
  "type": "openai_response",
  "session_id": "your-session-id",
  "model": "gpt-4",
  "duration_ms": 1234,
  "prompt_tokens": 150,
  "completion_tokens": 50,
  "total_tokens": 200,
  "timestamp": "2025-11-20T22:00:01Z"
}
```

*Error Message:*
```json
{
  "type": "error",
  "session_id": "your-session-id",
  "error": "Invalid message format"
}
```

**Testing with wscat:**
```bash
npm install -g wscat
wscat -c "ws://localhost:8000/ws?session_id=test123"
> {"type": "message", "session_id": "test123", "content": "Hello"}
```

**Telemetry:**
- Real-time events appear in WebSocket stream (<100ms latency)
- Historical telemetry available in [Jaeger UI](http://localhost:16686)

### Generate a Patient Clinical History

Request:
```bash
curl -X POST http://localhost:8000/patient \
  -H 'Content-Type: application/json' \
  -d '{"patient_id":"<FHIR Patient UUID>"}'
```

Example response (truncated):
```json
{
  "patient_id": "123e4567-e89b-12d3-a456-426614174000",
  "patient_name": "Jane Doe",
  "clinical_summary": "Patient with a history of hypertension and diabetes, currently stable.",
  "key_conditions": ["Hypertension", "Type 2 Diabetes Mellitus"],
  "active_medications": ["Lisinopril", "Metformin"],
  "recent_encounters": ["2025-11-01: Routine follow-up", "2025-10-10: Lab work"],
  "generated_at": "2025-11-14T20:00:00Z"
}
```

**⚠️ Security Warning:** WebSocket telemetry events may contain sensitive data including:
- OpenAI prompts and completions
- MCP FHIR queries and responses
- Potentially PHI (Protected Health Information)

**Current Configuration:**
- WebSocket connections accept any session_id (no authentication)
- CORS enabled for `localhost:3000` and `localhost:5173` (frontend dev servers)
- **Development only** - No authentication or encryption
- **Production requirements:** Use `wss://` (TLS), implement JWT authentication, add rate limiting, filter PHI from telemetry

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes
* In-memory sessions only; replace `ChatService` for persistence.
* Ensure Aidbox healthcheck passes; SSE endpoint is `http://localhost:8080/sse`.
