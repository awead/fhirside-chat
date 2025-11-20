# Epic 002: Front-End Chat Interface with Telemetry - Brownfield Enhancement

## Epic Goal

Provide users with an interactive web-based chat interface to communicate with the FHIRside Chat backend while visualizing real-time telemetry traces showing OpenAI API calls and Aidbox MCP server interactions.

## Epic Description

### Existing System Context

**Current relevant functionality:**
- FastAPI backend with `/chat` POST endpoint accepting `session_id` and `message`
- WebSocket endpoint at `/ws` for real-time chat (not used in v1)
- OpenTelemetry instrumentation sending traces to Jaeger (http://localhost:16686)
- PydanticAI agents making calls to Azure OpenAI and Aidbox FHIR server via MCP

**Technology stack:**
- Backend: Python 3.13, FastAPI, PydanticAI, OpenTelemetry
- Existing telemetry: Jaeger UI at localhost:16686
- No existing front-end (backend API only)

**Integration points:**
- REST API `/chat` endpoint (POST with JSON)
- OpenTelemetry OTLP exporter at http://localhost:4317
- Need to expose telemetry data to front-end via new API endpoint

### Enhancement Details

**What's being added/changed:**

1. **Web-based chat interface** - Single-page application with:
   - Chat input field and message history display
   - Session management (generate/reuse session IDs)
   - Modern, responsive UI following best UX practices

2. **Telemetry visualization panel** - Real-time display of:
   - OpenAI API calls (prompts, responses, token usage)
   - Aidbox MCP server queries and responses
   - Trace timing and span information
   - Error states and debugging information

3. **Backend telemetry API** - New endpoint to:
   - Query and expose OpenTelemetry trace data
   - Stream or poll traces for current chat session
   - Format trace data for front-end consumption

**How it integrates:**
- Front-end served as static assets (from `/static` or separate service)
- Calls existing `/chat` POST endpoint for message processing
- New `/telemetry` endpoint provides trace data for visualization
- WebSocket option for real-time trace streaming (optional for v1)

**Success criteria:**
- Users can send messages and see AI responses in a chat interface
- Telemetry panel shows OpenAI prompts/responses for each message
- Telemetry panel shows MCP queries to Aidbox server
- Trace data synchronized with corresponding chat messages
- UI is responsive and accessible on desktop browsers
- No degradation of existing API performance

## Stories

### Story 1: Backend Telemetry API Endpoint

Create a new FastAPI endpoint that exposes OpenTelemetry trace data for consumption by the front-end. This enables the UI to display real-time telemetry information.

**Key Tasks:**
- Design trace data export format (JSON schema for spans)
- Implement `/telemetry/{session_id}` GET endpoint to retrieve traces
- Query Jaeger backend or OpenTelemetry collector for trace data
- Filter traces by session ID and timestamp
- Add appropriate CORS headers for front-end access
- Document endpoint in FastAPI OpenAPI schema

**Acceptance Criteria:**
- Endpoint returns trace data for a given session ID
- Response includes OpenAI calls and MCP queries
- Response format is consumable by front-end (structured JSON)
- No performance impact on `/chat` endpoint

### Story 2: Chat UI Component

Build a modern, responsive chat interface using React (or similar framework) that communicates with the existing `/chat` API endpoint.

**Key Tasks:**
- Set up front-end build environment (Vite + React or Next.js)
- Create chat UI components (message list, input field, send button)
- Implement session ID generation and storage (localStorage)
- Connect to `/chat` POST endpoint for message submission
- Display conversation history with user/assistant message distinction
- Add loading states and error handling
- Style with TailwindCSS following modern design patterns
- Serve front-end via FastAPI static file serving or separate dev server

**Acceptance Criteria:**
- Users can type messages and receive responses
- Session persists across page reloads
- Messages display with clear user/assistant distinction
- Loading indicator shown while waiting for response
- Error messages displayed for API failures
- UI is responsive on desktop and tablet screen sizes

### Story 3: Telemetry Visualization Panel

Integrate a telemetry visualization panel into the chat interface that displays OpenAI and Aidbox traces for each message interaction.

**Key Tasks:**
- Create telemetry panel component adjacent to chat UI
- Connect to `/telemetry/{session_id}` endpoint
- Parse and display OpenAI span data (prompts, completions, token counts)
- Parse and display MCP span data (FHIR queries, responses)
- Implement collapsible/expandable trace details
- Correlate traces with specific chat messages (by timestamp/span ID)
- Add refresh/auto-refresh functionality for trace updates
- Style trace data for readability (syntax highlighting, structured display)

**Acceptance Criteria:**
- Telemetry panel displays traces for current session
- OpenAI API calls visible with prompt and response content
- Aidbox MCP queries visible with request/response details
- Traces can be expanded/collapsed for detailed inspection
- Panel updates when new messages are sent
- Clear visual correlation between messages and their traces
- Trace data formatted for developer readability

## Compatibility Requirements

- [x] Existing `/chat` API endpoint remains unchanged
- [x] Existing `/patient` API endpoint unaffected
- [x] No changes to existing telemetry instrumentation
- [x] Front-end is optional - API remains functional without it
- [x] Performance impact is minimal (telemetry queries are read-only)
- [x] CORS configuration added without breaking existing API consumers

## Risk Mitigation

**Primary Risk:** Exposing telemetry data (including OpenAI prompts/responses) to front-end could leak sensitive information

**Mitigation:**
- Telemetry endpoint only accessible on localhost development environment
- Add authentication/authorization before production deployment
- Filter sensitive data from traces (API keys, patient PHI)
- Document security considerations in README

**Secondary Risk:** Front-end build complexity adds overhead to development workflow

**Mitigation:**
- Use modern tooling (Vite) with hot reload for fast iteration
- Separate front-end and backend development concerns
- Document front-end setup in README
- Make front-end optional - backend remains usable via curl/Postman

**Rollback Plan:**
- Remove `/telemetry` endpoint if issues arise
- Revert static file serving configuration
- Backend `/chat` API continues to work independently

## Definition of Done

- [x] `/telemetry` API endpoint implemented and tested
- [x] Chat UI component functional with message send/receive
- [x] Telemetry panel displays OpenAI and Aidbox traces
- [x] All stories completed with acceptance criteria met
- [x] Existing `/chat` endpoint verified through testing
- [x] Front-end build process documented in README
- [x] No regression in existing API functionality
- [x] Manual testing with real OpenAI and Aidbox interactions completed

## Handoff Notes

### Technical Context

**Existing Patterns to Follow:**
- Async FastAPI endpoints with Pydantic models (`@app.get`, `@app.post`)
- OpenTelemetry instrumentation already in place via `instrumentation()`
- Standard error handling with `HTTPException`
- Environment-based configuration (API keys, endpoints)

**Key Integration Points:**
- `/chat` endpoint: `POST` with `ChatRequest` model (`session_id`, `message`)
- OpenTelemetry: Spans exported to Jaeger at localhost:4317
- Trace data: May need to query Jaeger Query API or OpenTelemetry Collector

**Critical Compatibility Requirements:**
- Must not modify existing `ChatService` or `chat_agent()` behavior
- CORS middleware needs to be added to `create_app()` for front-end access
- Static file serving should use FastAPI's `StaticFiles` mount
- Session IDs must match between chat API and telemetry API

**Front-End Technology Recommendations:**
- **Framework:** React with Vite (fast dev server, modern tooling)
- **Styling:** TailwindCSS (utility-first, matches modern design patterns)
- **Components:** shadcn/ui or Headless UI (accessible, pre-built components)
- **Icons:** Lucide React (modern icon set)
- **HTTP Client:** Fetch API or Axios for REST calls

Each story must include verification that existing `/chat` functionality remains intact.

## Success Metrics

**User Experience:**
- Users can have a conversation with the AI agent via web UI
- Developers can inspect trace data without switching to Jaeger UI
- Telemetry provides debugging value for understanding AI agent behavior

**Technical Quality:**
- Chat latency remains unchanged (< 5s for typical responses)
- Telemetry queries complete in < 1s
- No errors introduced in existing endpoints
- Code follows existing project style (ruff formatting, pytest tests)

**Documentation:**
- README updated with front-end setup instructions
- Telemetry endpoint documented in OpenAPI schema
- Security considerations documented for telemetry exposure
