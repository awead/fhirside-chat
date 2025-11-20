# Epic 003: Real-Time WebSocket Chat & Telemetry Migration - Brownfield Enhancement

**Status:** 📋 Ready for Development
**Created:** 2025-11-20

## Epic Goal

Replace REST-based polling with WebSocket real-time communication for chat and telemetry, eliminating 5-6 second Jaeger query delays and providing instant visibility into agent operations for improved developer debugging experience.

## Epic Description

### Existing System Context

**Current relevant functionality:**
- FastAPI backend with REST POST `/chat` endpoint and GET `/telemetry/{session_id}` polling
- Minimal WebSocket `/ws` endpoint exists (lines 87-97 in src/app.py) but not fully utilized
- React 18 frontend with REST fetch calls and 5-second polling for telemetry
- OpenTelemetry instrumentation with 5-6 second batch export delay to Jaeger
- PydanticAI agents making calls to Azure OpenAI and Aidbox MCP server

**Technology stack:**
- Backend: Python 3.13, FastAPI, PydanticAI, Azure OpenAI, fastmcp, OpenTelemetry/Jaeger
- Frontend: React 18, TypeScript, Vite, TailwindCSS, shadcn/ui
- Deployment: Docker Compose (Aidbox, PostgreSQL, Jaeger), Uvicorn (FastAPI), Vite dev server

**Integration points:**
- Enhance existing `/ws` WebSocket endpoint for full message routing
- Add telemetry emission hooks in PydanticAI agent tool execution
- Replace frontend REST calls with WebSocket client
- Maintain POST `/patient` endpoint (out of scope, unaffected)

**Problem Statement:**
- Telemetry data is "delayed and incorrect, often nil"
- 5-6 second delay from OpenTelemetry batch export to Jaeger
- REST polling creates race conditions and stale data
- Poor developer debugging experience

### Enhancement Details

**What's being added/changed:**

1. **Backend WebSocket Infrastructure:**
   - ConnectionManager for WebSocket connection lifecycle and session correlation
   - Enhanced `/ws` endpoint with JSON message routing and Pydantic validation
   - WebSocket message protocol models (UserMessage, AssistantMessage, ToolCallEvent, etc.)
   - Session management via query parameters (`/ws?session_id=xxx`)

2. **Real-Time Telemetry Emission:**
   - TelemetryEmitter for fire-and-forget event broadcasting (non-blocking)
   - Hooks into PydanticAI agent tool execution
   - Emit tool_call, tool_result, openai_call events as they occur
   - **Dual emission:** WebSocket (real-time <100ms) + Jaeger export (historical analysis)

3. **Frontend WebSocket Client:**
   - useWebSocket custom React hook with connection management
   - Automatic reconnection with exponential backoff
   - TypeScript WebSocket message types (discriminated unions)
   - ConnectionStatus indicator component (connected/disconnected/reconnecting)

4. **Streaming UI Updates:**
   - ChatContainer handles streaming message display (progressive text rendering)
   - TelemetryPanel consumes real-time events (removes polling/refresh)
   - StreamingMessage component for ChatGPT-style typing effect
   - Maintains accessibility compliance (WCAG 2.1 AA)

5. **Migration Cleanup:**
   - Deprecate and remove REST POST `/chat` endpoint
   - Remove GET `/telemetry/{session_id}` endpoint (replaced by WebSocket)
   - Remove deprecated chatApi.ts and telemetryApi.ts
   - Update documentation with WebSocket usage

**How it integrates:**
- WebSocket runs on same port as HTTP (8000) via native Uvicorn support
- Frontend connects to `ws://localhost:8000/ws?session_id=xxx`
- ConnectionManager maps WebSocket connections to session_ids
- TelemetryEmitter broadcasts events to specific session via ConnectionManager
- OpenTelemetry continues exporting to Jaeger (parallel to WebSocket emission)
- POST `/patient` endpoint completely unaffected (separate code path)

**Success criteria:**
- Telemetry latency reduces from 5-6 seconds to <100ms
- Zero data loss during connection drops (reconnection works)
- Session isolation verified (no cross-session data leakage)
- Streaming chat responses provide better UX
- All 40+ existing tests pass (no regressions)
- Accessibility compliance maintained
- Zero infrastructure changes required

## Architecture & Technical Design

### Tech Stack (No New Dependencies)

All capabilities exist in current stack:
- **FastAPI:** Native WebSocket support ✅
- **React:** Native `WebSocket` API ✅
- **Uvicorn:** Native WebSocket support ✅
- **Pydantic:** Message validation ✅
- **TypeScript:** Type-safe messages ✅

**Rationale:** WebSocket is standard protocol, no external libraries needed (socket.io, etc.)

### WebSocket Message Protocol

**Client → Server:**
```python
class UserMessage(BaseModel):
    type: Literal["message"]
    session_id: str
    content: str
```

**Server → Client:**
```python
class AssistantMessage(BaseModel):
    type: Literal["assistant"]
    session_id: str
    content: str
    streaming: bool = False

class ToolCallEvent(BaseModel):
    type: Literal["tool_call"]
    session_id: str
    tool_call_id: str
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: datetime

class ToolResultEvent(BaseModel):
    type: Literal["tool_result"]
    session_id: str
    tool_call_id: str
    tool_name: str
    result: str
    duration_ms: int
    timestamp: datetime

class OpenAIEvent(BaseModel):
    type: Literal["openai_call"] | Literal["openai_response"]
    session_id: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    duration_ms: Optional[int] = None
    timestamp: datetime

class ErrorMessage(BaseModel):
    type: Literal["error"]
    session_id: str
    error: str

class ConnectionStatus(BaseModel):
    type: Literal["connection"]
    status: Literal["connected", "disconnected", "reconnecting"]
    session_id: str
```

**Frontend TypeScript:** Mirror Python models with discriminated unions

### Component Architecture

**New Components:**

**1. ConnectionManager** (`src/websocket/connection_manager.py`)
- Manage WebSocket connections by session_id
- Broadcast messages to specific session or all
```python
class ConnectionManager:
    async def connect(self, websocket: WebSocket, session_id: str)
    async def disconnect(self, session_id: str)
    async def send_message(self, session_id: str, message: WebSocketMessage)
```

**2. TelemetryEmitter** (`src/telemetry/event_emitter.py`)
- Fire-and-forget telemetry emission (non-blocking)
- Hook into PydanticAI agent tool execution
```python
class TelemetryEmitter:
    async def emit_tool_call(self, session_id: str, tool_name: str, args: dict)
    async def emit_tool_result(self, session_id: str, tool_name: str, result: str, duration_ms: int)
    async def emit_openai_call(self, session_id: str, model: str, tokens: dict)
```

**3. useWebSocket Hook** (`frontend/src/hooks/useWebSocket.ts`)
- Connection management, reconnection (exponential backoff)
- Message parsing, state management
```typescript
interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (content: string) => void;
  messages: Message[];
  telemetryEvents: TelemetryEvent[];
  error: string | null;
}
```

**4. StreamingMessage Component** (`frontend/src/components/StreamingMessage.tsx`)
- Progressive text rendering for `streaming: true`

**5. ConnectionStatus Component** (`frontend/src/components/ConnectionStatus.tsx`)
- Visual connection indicator (connected/disconnected/reconnecting)

**Modified Components:**
- **Enhanced `/ws`** - Full message routing, Pydantic validation
- **ChatService** - Add telemetry hooks during agent execution
- **ChatContainer** - Handle streaming messages
- **TelemetryPanel** - Real-time events (remove polling)

**Component Interaction:**
```
Frontend (React)
  └── useWebSocket Hook → Native WebSocket
       └── ChatContainer + TelemetryPanel

            ↓ ws:// (bidirectional) ↓

Backend (FastAPI)
  └── /ws Endpoint
       ├── ConnectionManager
       └── ChatService + TelemetryEmitter
            ├── PydanticAI Agent
            │    ├── Azure OpenAI
            │    └── Aidbox MCP
            └── OpenTelemetry (dual: WebSocket + Jaeger)
                     └── Jaeger (historical)
```

### File Organization

**New Files:**
```
src/
├── models/websocket_messages.py          # NEW: Protocol models
├── websocket/
│   ├── __init__.py                       # NEW
│   └── connection_manager.py             # NEW
└── telemetry/event_emitter.py            # NEW

frontend/src/
├── hooks/useWebSocket.ts                 # NEW
├── types/websocket.ts                    # NEW
└── components/
    ├── StreamingMessage.tsx              # NEW
    └── ConnectionStatus.tsx              # NEW

tests/
├── websocket/
│   ├── test_connection_manager.py        # NEW
│   └── test_websocket_messages.py        # NEW
├── telemetry/test_event_emitter.py       # NEW
└── e2e/test_websocket_e2e.py             # NEW
```

**Modified Files:**
```
src/app.py                                # Enhanced /ws, deprecated /chat
src/ai/agents.py                          # Add telemetry hooks
frontend/src/App.tsx                      # Use useWebSocket
frontend/src/components/ChatContainer.tsx # Streaming
frontend/src/components/telemetry/TelemetryPanel.tsx  # Real-time
```

**Deprecated Files (Remove in Story 010):**
```
src/models/telemetry.py                   # Old Jaeger models
frontend/src/services/chatApi.ts          # REST client
frontend/src/services/telemetryApi.ts     # REST polling
```

### Infrastructure & Deployment

**Infrastructure Changes:** **NONE**

- Uvicorn has native WebSocket (same port 8000)
- Docker Compose unchanged (Aidbox, PostgreSQL, Jaeger)
- Same startup: `uv run uvicorn src:app --port 8000 --reload`

**Vite Config Update:**
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
});
```

**Rollback Strategy:**
- Phase 1: Backend only → REST still works
- Phase 2: Frontend switches → Deprecated `/chat` available
- Phase 3: Remove deprecated → After validation

### Testing Strategy

**Coverage:**
- **Overall:** 80%+ (maintain existing standard)
- **ConnectionManager:** 90%+ (critical infrastructure)
- **Frontend useWebSocket:** 85%+

**Unit Tests:**
```python
# Backend
test_connection_manager.py - connect, disconnect, send, broadcast
test_event_emitter.py - emit methods, fire-and-forget
test_websocket_messages.py - Pydantic validation

# Frontend
useWebSocket.test.ts - connection, reconnection, parsing
Component tests - streaming, status, telemetry
```

**Integration Tests:**
```python
test_websocket_connect_and_disconnect()
test_websocket_message_routing()
test_websocket_telemetry_emission()
test_multiple_concurrent_sessions()
```

**E2E Tests:**
```python
test_websocket_chat_with_real_services()  # Full flow with Aidbox/OpenAI
test_websocket_reconnection()             # Connection recovery
test_websocket_session_isolation()        # No cross-contamination
```

**Regression:**
- All 40 existing tests must pass
- POST `/patient` verified unaffected
- Accessibility compliance maintained

### Security Considerations

**Current:** No auth/authz (development environment)

**WebSocket Security:**
- **Development:** `ws://` acceptable (localhost)
- **Production:** `wss://` REQUIRED (TLS)
- **Session:** Client UUID (no validation) - accept risk for dev
- **Protection:** Pydantic validation, CORS enforcement, session isolation tests

**Future (Production):**
- JWT authentication with session_id claim
- Connection limits per IP
- Rate limiting middleware

### Key Architectural Decisions

1. **No new external dependencies** - Native WebSocket support in FastAPI/React
2. **Zero infrastructure changes** - Uvicorn handles WebSocket on same port
3. **Dual telemetry emission** - WebSocket (real-time) + Jaeger (historical)
4. **Fire-and-forget emission** - Non-blocking to avoid impacting agent performance
5. **Phased migration** - Deprecated endpoints kept during rollout for safety

## Stories

This epic has been broken down into five detailed, properly-scoped stories for iterative, safe implementation.

### Story 006: Backend WebSocket Infrastructure

**File:** `docs/stories/story-006-backend-websocket-infrastructure.md`
**Effort:** 5 Story Points (~8-10 hours)
**Status:** Ready for Development
**Dependencies:** None

Implement ConnectionManager for WebSocket lifecycle management, enhance existing `/ws` endpoint with full message routing, create WebSocket message Pydantic models, add comprehensive unit tests.

**Key Deliverables:**
- `src/websocket/connection_manager.py` - ConnectionManager class
- `src/models/websocket_messages.py` - Message protocol models
- Enhanced `/ws` endpoint in `src/app.py` with JSON routing and Pydantic validation
- Unit tests: `test_connection_manager.py`, `test_websocket_messages.py`
- 90%+ test coverage for ConnectionManager (critical infrastructure)

**Integration Checkpoint:** Manual WebSocket testing with wscat or Postman

---

### Story 007: Real-Time Telemetry Emission

**File:** `docs/stories/story-007-realtime-telemetry-emission.md`
**Effort:** 5 Story Points (~8-10 hours)
**Status:** Ready for Development
**Dependencies:** Story 006 (ConnectionManager required)

Implement TelemetryEmitter for fire-and-forget event broadcasting, hook into PydanticAI agent tool execution, emit tool_call/tool_result/openai_call events, maintain parallel OpenTelemetry export to Jaeger.

**Key Deliverables:**
- `src/telemetry/event_emitter.py` - TelemetryEmitter class
- Hooks in ChatService for agent tool execution telemetry
- Emit ToolCallEvent, ToolResultEvent, OpenAIEvent via WebSocket
- Parallel OpenTelemetry → Jaeger export maintained
- Unit tests: `test_event_emitter.py`

**Integration Checkpoint:** Verify events appear in WebSocket stream AND Jaeger UI

---

### Story 008: Frontend WebSocket Client

**File:** `docs/stories/story-008-frontend-websocket-client.md`
**Effort:** 5 Story Points (~8-10 hours)
**Status:** Ready for Development
**Dependencies:** Story 006 (Backend WebSocket infrastructure)

Create useWebSocket custom React hook with connection management, implement TypeScript WebSocket message types, add reconnection logic with exponential backoff, create ConnectionStatus indicator component.

**Key Deliverables:**
- `frontend/src/hooks/useWebSocket.ts` - Custom hook with connection management
- `frontend/src/types/websocket.ts` - TypeScript message types (discriminated unions)
- `frontend/src/components/ConnectionStatus.tsx` - Connection indicator (Wifi icon)
- Reconnection logic with exponential backoff (max 30 seconds)
- Vite config update for WebSocket proxy (`ws: true`)
- Hook tests: `useWebSocket.test.ts`

**Integration Checkpoint:** Frontend successfully connects to backend WebSocket

---

### Story 009: Streaming UI Updates

**File:** `docs/stories/story-009-streaming-ui-updates.md`
**Effort:** 3 Story Points (~5-6 hours)
**Status:** Ready for Development
**Dependencies:** Stories 006 (Backend), 007 (Telemetry), 008 (Frontend Client)

Modify ChatContainer for streaming message display, update TelemetryPanel for real-time events (remove polling), create StreamingMessage component, verify accessibility compliance maintained.

**Key Deliverables:**
- Modified `ChatContainer.tsx` - Handle streaming messages (progressive text)
- Modified `TelemetryPanel.tsx` - Real-time events (remove polling/refresh)
- New `StreamingMessage.tsx` - Progressive text rendering component
- Updated `App.tsx` - Use useWebSocket instead of REST calls
- Accessibility verification (screen reader, keyboard navigation)
- Component tests for streaming behavior

**Integration Checkpoint:** End-to-end chat with real-time telemetry working

---

### Story 010: WebSocket Migration Cleanup

**File:** `docs/stories/story-010-websocket-migration-cleanup.md`
**Effort:** 3 Story Points (~5-6 hours)
**Status:** Ready for Development
**Dependencies:** All previous stories (006-009) must be complete and validated

Remove deprecated REST `/chat` endpoint, remove GET `/telemetry/{session_id}` endpoint, remove deprecated frontend REST clients, update README documentation, full regression test validation.

**Key Deliverables:**
- Remove deprecated POST `/chat` endpoint from `src/app.py`
- Remove GET `/telemetry/{session_id}` endpoint
- Remove `src/models/telemetry.py` (old Jaeger models)
- Remove `frontend/src/services/chatApi.ts` and `telemetryApi.ts`
- Update `README.md` with WebSocket usage examples
- Full regression test suite passes (40+ tests)
- Clean codebase with no deprecated code

**Completion Checkpoint:** Epic 003 Definition of Done satisfied

---

## Compatibility Requirements

- [ ] POST `/patient` endpoint remains completely unchanged
- [ ] WebSocket `/ws` enhanced but maintains query parameter session management
- [ ] Static file serving unchanged (frontend dist mounting)
- [ ] CORS middleware configuration unchanged (localhost origins)
- [ ] OpenTelemetry export to Jaeger continues (parallel to WebSocket)
- [ ] All existing functionality works identically from user perspective
- [ ] Performance improves (5-6s → <100ms telemetry, remove polling overhead)
- [ ] No infrastructure changes required (Uvicorn native WebSocket)

## Risk Mitigation

**Primary Risk:** WebSocket connection instability (network issues, server restarts)

**Mitigation:**
- Automatic reconnection with exponential backoff (frontend useWebSocket hook)
- Connection status indicator (users see connection state clearly)
- Graceful degradation messaging ("Reconnecting..." state)
- Session recovery: Frontend resends session_id on reconnect
- Server-side: ConnectionManager handles disconnect cleanup properly

**Secondary Risk:** Breaking existing REST consumers (if any external clients use `/chat`)

**Mitigation:**
- Mark POST `/chat` as deprecated but keep functional during migration (Stories 006-009)
- Add deprecation warnings in API responses
- Monitor `/chat` usage metrics before removal
- Only remove in Story 010 after full validation period
- Rollback plan: Git revert + revert frontend to REST calls

**Tertiary Risk:** Session isolation bugs (cross-session data leakage)

**Mitigation:**
- Comprehensive session isolation tests (`test_websocket_session_isolation`)
- ConnectionManager session mapping thoroughly tested (90%+ coverage)
- E2E tests with multiple concurrent connections
- Manual testing with multiple browser tabs

**Rollback Plan:**
- **Phase 1 (Stories 006-007):** Backend only, REST still works → Zero user impact
- **Phase 2 (Stories 008-009):** Frontend switches, deprecated `/chat` available → Quick revert possible
- **Phase 3 (Story 010):** Remove deprecated → Only after production-like validation complete
- No database migrations to reverse (in-memory sessions)

## Definition of Done

### All Stories Complete

- [ ] Story 006: Backend WebSocket Infrastructure (all acceptance criteria met, checkpoint passed)
- [ ] Story 007: Real-Time Telemetry Emission (all acceptance criteria met, checkpoint passed)
- [ ] Story 008: Frontend WebSocket Client (all acceptance criteria met, checkpoint passed)
- [ ] Story 009: Streaming UI Updates (all acceptance criteria met, checkpoint passed)
- [ ] Story 010: WebSocket Migration Cleanup (all acceptance criteria met, checkpoint passed)

### Functional Requirements

- [ ] WebSocket `/ws` endpoint fully functional with message routing
- [ ] ConnectionManager manages WebSocket lifecycle correctly
- [ ] TelemetryEmitter broadcasts events in real-time (<100ms latency)
- [ ] useWebSocket hook handles connection/reconnection/errors
- [ ] Chat UI displays streaming messages progressively
- [ ] TelemetryPanel shows real-time events (no polling)
- [ ] Connection status indicator works (connected/disconnected/reconnecting)
- [ ] Session isolation verified (no cross-session data leakage)
- [ ] Deprecated REST endpoints removed cleanly

### Quality Requirements

- [ ] All 40+ existing tests pass (zero regressions)
- [ ] New tests achieve 80%+ coverage for new code
- [ ] ConnectionManager achieves 90%+ test coverage (critical infrastructure)
- [ ] useWebSocket hook achieves 85%+ test coverage
- [ ] Integration tests pass (message routing, telemetry emission, concurrent sessions)
- [ ] E2E tests pass with real services (Aidbox, OpenAI, Jaeger)
- [ ] POST `/patient` endpoint verified unaffected through testing
- [ ] Accessibility compliance maintained (WCAG 2.1 AA)
- [ ] Lighthouse Accessibility score ≥ 90
- [ ] axe DevTools reports 0 critical violations
- [ ] No performance degradation on existing API
- [ ] Telemetry latency <100ms verified (vs. 5-6 seconds previously)

### Documentation

- [ ] Architecture document complete (`docs/epics/epic-003-websocket-architecture.md`)
- [ ] All 5 story documents created with detailed acceptance criteria
- [ ] README updated with WebSocket connection examples
- [ ] WebSocket message protocol documented
- [ ] Migration guide available for developers
- [ ] Security considerations documented (connection limits, auth for production)

### Integration Testing

- [ ] End-to-end chat flow with real Aidbox and Azure OpenAI
- [ ] Telemetry events appear in WebSocket stream AND Jaeger UI (dual emission verified)
- [ ] Connection drop and recovery tested (reconnection works)
- [ ] Multiple concurrent users tested (session isolation verified)
- [ ] Load testing with 10 concurrent WebSocket connections (development baseline)
- [ ] Frontend WebSocket proxy working in Vite dev mode
- [ ] Production build tested with static file serving from FastAPI

### Deployment Verification

- [ ] Docker Compose services start correctly (Aidbox, PostgreSQL, Jaeger)
- [ ] Backend starts with `uv run uvicorn src:app --port 8000 --reload`
- [ ] Frontend dev server starts with `npm run dev`
- [ ] WebSocket connections work on ws://localhost:8000/ws
- [ ] Jaeger UI accessible at http://localhost:16686 (historical traces)
- [ ] No new environment variables required
- [ ] No new service dependencies added

### Success Metrics

- [ ] **Telemetry Latency:** Reduced from 5-6 seconds to <100ms (measured)
- [ ] **Connection Reliability:** Reconnection success rate >95% (manual testing)
- [ ] **Session Isolation:** Zero cross-session data leakage (E2E tests)
- [ ] **Developer Experience:** Positive feedback on real-time telemetry visibility
- [ ] **Code Quality:** 80%+ test coverage maintained across project
- [ ] **Zero Downtime:** Migration completed without service interruption

## Timeline & Effort

**Total Effort:** ~21 Story Points (~36-42 hours of development)
**Estimated Timeline:** 3-4 weeks with 1 developer

**Story Sequence:**
1. **Week 1:** Story 006 (Backend Infrastructure) + Story 007 (Telemetry Emission)
2. **Week 2:** Story 008 (Frontend Client) + Story 009 (Streaming UI)
3. **Week 3:** Story 010 (Migration Cleanup) + Integration Testing
4. **Week 4:** Final validation, documentation, production readiness

**Critical Path:**
- Story 006 must complete before 007 and 008
- Stories 007 and 008 can run in parallel after 006
- Story 009 requires 006, 007, 008 complete
- Story 010 requires all previous stories validated

## Stakeholder Communication

**Development Team:**
- Architecture document provides complete technical guidance
- Story documents have detailed acceptance criteria
- Testing strategy defined with coverage requirements
- Migration is phased for safety (rollback at each phase)

**Product/Business:**
- Improved developer debugging experience (5-6s → <100ms telemetry)
- Better user experience (streaming chat responses)
- Zero infrastructure cost increase
- Zero breaking changes for end users
- Low risk with phased rollout

**Operations:**
- No infrastructure changes required
- Same Docker Compose setup
- Same deployment process
- WebSocket scales with existing Uvicorn setup
- Production considerations documented (sticky sessions, Redis for scaling)

## Related Documents

- **Architecture:** `docs/epics/epic-003-websocket-architecture.md` (complete technical design)
- **Epic 001:** `docs/epics/epic-001-patient-history-enhancement.md` (unaffected, preserved)
- **Epic 002:** `docs/epics/epic-002-frontend-chat-interface.md` (current REST implementation being replaced)
- **Story Documents:** `docs/stories/story-006-*.md` through `story-010-*.md` (to be created by Scrum Master)

---

**Epic Status:** 📋 Ready for Story Creation

**Next Steps:**
1. Scrum Master creates 5 detailed story documents (006-010)
2. Development team reviews architecture and story acceptance criteria
3. Sprint planning to sequence stories (recommend: 006→007→008→009→010)
4. Begin Story 006 (Backend WebSocket Infrastructure)

**Epic Owner:** John (Product Manager)
**Technical Lead:** Winston (Architect)
**Created:** 2025-11-20
