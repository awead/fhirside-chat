# Story 007: Real-Time Telemetry Emission

**Status:** Draft
**Epic:** 003 - Real-Time WebSocket Chat & Telemetry
**Story Points:** 5
**Estimated Hours:** 8-10 hours
**Dependencies:** Story 006 (ConnectionManager required)

## Story

**As a** backend developer,
**I want** to emit telemetry events in real-time via WebSocket as they occur,
**so that** the frontend receives immediate visibility into agent operations without polling delays.

## Acceptance Criteria

1. **TelemetryEmitter Implementation**
   - TelemetryEmitter class created in `src/telemetry/event_emitter.py`
   - Fire-and-forget async methods (non-blocking)
   - Emits events via ConnectionManager to specific session
   - Methods: `emit_tool_call()`, `emit_tool_result()`, `emit_openai_call()`
   - Handles ConnectionManager errors gracefully (logs warning, doesn't crash)

2. **PydanticAI Agent Telemetry Hooks**
   - ChatService enhanced with telemetry emission hooks
   - Emit ToolCallEvent when agent invokes a tool
   - Emit ToolResultEvent when tool execution completes
   - Emit OpenAIEvent for Azure OpenAI API calls
   - Include timing information (duration_ms)
   - Include relevant metadata (tool_name, model, token counts)

3. **Dual Telemetry Emission**
   - WebSocket real-time emission working (<100ms latency)
   - Existing OpenTelemetry → Jaeger export UNCHANGED
   - Both telemetry streams active simultaneously
   - WebSocket for real-time display, Jaeger for historical analysis
   - No performance degradation from dual emission

4. **Unit Tests**
   - `tests/telemetry/test_event_emitter.py` created
   - Test each emit method with valid data
   - Test fire-and-forget behavior (doesn't block)
   - Test graceful error handling (disconnected session)
   - Mock ConnectionManager to verify calls
   - Achieve 80%+ test coverage

5. **Integration Checkpoint**
   - WebSocket client receives ToolCallEvent during agent execution
   - WebSocket client receives ToolResultEvent after tool completes
   - WebSocket client receives OpenAIEvent for LLM calls
   - Events visible in WebSocket stream (<100ms latency)
   - Events also visible in Jaeger UI (existing 5-6s delay)
   - Verify with manual WebSocket connection (wscat)

## Tasks / Subtasks

- [ ] **Task 1: Implement TelemetryEmitter Class** (AC: 1)
  - [ ] Create `src/telemetry/` directory if not exists
  - [ ] Create `src/telemetry/event_emitter.py`
  - [ ] Define `TelemetryEmitter` class with ConnectionManager dependency injection
  - [ ] Implement `async def emit_tool_call(session_id: str, tool_call_id: str, tool_name: str, arguments: dict)`
  - [ ] Implement `async def emit_tool_result(session_id: str, tool_call_id: str, tool_name: str, result: str, duration_ms: int)`
  - [ ] Implement `async def emit_openai_call(session_id: str, model: str, prompt_tokens: int, completion_tokens: int, duration_ms: int)`
  - [ ] Each method creates appropriate message model (ToolCallEvent, ToolResultEvent, OpenAIEvent)
  - [ ] Each method calls `ConnectionManager.send_message()` wrapped in try/except
  - [ ] Log warning if send fails (session disconnected), don't raise exception
  - [ ] Add timestamp to all events using `datetime.now()`

- [ ] **Task 2: Add Telemetry Hooks to ChatService** (AC: 2)
  - [ ] Import TelemetryEmitter in `src/app.py` or `src/ai/agents.py`
  - [ ] Create global TelemetryEmitter instance with ConnectionManager
  - [ ] Identify PydanticAI agent tool call locations in ChatService
  - [ ] Before tool execution: emit ToolCallEvent with tool_name and arguments
  - [ ] After tool execution: emit ToolResultEvent with result and duration
  - [ ] Wrap agent.run() or similar with timing: `start = time.time()`, `duration_ms = (time.time() - start) * 1000`
  - [ ] For Azure OpenAI calls: emit OpenAIEvent with model and token counts (if available from response)
  - [ ] Test hooks don't break existing chat functionality

- [ ] **Task 3: Verify Dual Telemetry (WebSocket + Jaeger)** (AC: 3)
  - [ ] Confirm existing OpenTelemetry instrumentation still active
  - [ ] Verify Jaeger exporter configuration unchanged in `src/app.py`
  - [ ] Send test chat message: "What is quintin cole's diagnosis?"
  - [ ] Verify ToolCallEvent/ToolResultEvent appear in WebSocket
  - [ ] Verify same events appear in Jaeger UI (http://localhost:16686)
  - [ ] Measure WebSocket latency (should be <100ms)
  - [ ] Confirm existing 40+ tests still pass (no regression)
  - [ ] Verify POST `/patient` endpoint unaffected

- [ ] **Task 4: Create Unit Tests** (AC: 4)
  - [ ] Create `tests/telemetry/test_event_emitter.py`
  - [ ] Write test for `emit_tool_call()`:
    - [ ] Mock ConnectionManager
    - [ ] Call emit_tool_call with test data
    - [ ] Verify ConnectionManager.send_message called with ToolCallEvent
    - [ ] Verify event has correct type="tool_call"
    - [ ] Verify timestamp is present
  - [ ] Write test for `emit_tool_result()`:
    - [ ] Mock ConnectionManager
    - [ ] Call emit_tool_result with test data
    - [ ] Verify ToolResultEvent sent
    - [ ] Verify duration_ms included
  - [ ] Write test for `emit_openai_call()`:
    - [ ] Mock ConnectionManager
    - [ ] Call emit_openai_call with token counts
    - [ ] Verify OpenAIEvent sent with model and tokens
  - [ ] Write test for error handling:
    - [ ] Mock ConnectionManager.send_message to raise exception
    - [ ] Call emit methods
    - [ ] Verify exception caught and logged (doesn't propagate)
  - [ ] Run coverage: `pytest --cov=src/telemetry --cov-report=term-missing`
  - [ ] Verify 80%+ coverage

- [ ] **Task 5: Integration Testing & Checkpoint** (AC: 5)
  - [ ] Start all services: `docker compose up -d` (Aidbox, PostgreSQL, Jaeger)
  - [ ] Start backend: `uv run uvicorn src:app --port 8000 --reload`
  - [ ] Connect wscat: `wscat -c "ws://localhost:8000/ws?session_id=test123"`
  - [ ] Send chat message: `{"type": "message", "session_id": "test123", "content": "What is quintin cole's diagnosis?"}`
  - [ ] Observe WebSocket stream for:
    - [ ] ToolCallEvent (patient data retrieval)
    - [ ] ToolResultEvent (with FHIR data)
    - [ ] OpenAIEvent (Azure OpenAI call)
  - [ ] Measure time between sending message and receiving ToolCallEvent (<100ms target)
  - [ ] Open Jaeger UI: http://localhost:16686
  - [ ] Search for trace with session_id "test123"
  - [ ] Verify same events visible in Jaeger (5-6s delay expected)
  - [ ] Document manual testing results

## Dev Notes

### Previous Story Insights
- **Story 006** implemented ConnectionManager and WebSocket message models
- ConnectionManager provides `send_message(session_id, message)` method for targeted delivery
- WebSocket message protocol supports ToolCallEvent, ToolResultEvent, OpenAIEvent
- Session isolation tested and verified in Story 006

### TelemetryEmitter Component Specification
[Source: Epic 003, Section "Component Architecture"]

**Purpose:** Fire-and-forget telemetry emission (non-blocking) to avoid impacting agent performance

**Class Interface:**
```python
class TelemetryEmitter:
    def __init__(self, connection_manager: ConnectionManager)

    async def emit_tool_call(self, session_id: str, tool_name: str, args: dict) -> None
    async def emit_tool_result(self, session_id: str, tool_name: str, result: str, duration_ms: int) -> None
    async def emit_openai_call(self, session_id: str, model: str, tokens: dict) -> None
```

**Implementation Details:**
- Accept ConnectionManager via dependency injection (constructor)
- Each emit method constructs appropriate Pydantic message model
- Add `timestamp = datetime.now()` to all events
- Call `await connection_manager.send_message(session_id, event_model)`
- Wrap send_message in try/except (session might be disconnected)
- Log warning on error, don't raise exception (fire-and-forget pattern)
- Methods should be async but non-blocking (no heavy computation)

### PydanticAI Agent Hook Points
[Source: src/ai/agents.py and Epic 003 requirements]

The agent uses PydanticAI with Azure OpenAI. Telemetry should hook into:

1. **Tool Call Start:**
   - When agent decides to call a tool (e.g., fetch_patient_data)
   - Emit ToolCallEvent with tool_name, tool_call_id (generate UUID), arguments

2. **Tool Call Complete:**
   - After tool execution finishes
   - Emit ToolResultEvent with tool_call_id (match to call), result, duration_ms

3. **Azure OpenAI API Call:**
   - When agent makes LLM request
   - Emit OpenAIEvent with type="openai_call", model name
   - After LLM response received: Emit OpenAIEvent with type="openai_response", token counts, duration_ms

**Timing Pattern:**
```python
import time

start_time = time.time()
# ... tool execution or API call ...
duration_ms = int((time.time() - start_time) * 1000)
```

### WebSocket Message Models Reference
[Source: Story 006, src/models/websocket_messages.py]

```python
class ToolCallEvent(BaseModel):
    type: Literal["tool_call"]
    session_id: str
    tool_call_id: str  # Generate with str(uuid.uuid4())
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: datetime

class ToolResultEvent(BaseModel):
    type: Literal["tool_result"]
    session_id: str
    tool_call_id: str  # Match to ToolCallEvent
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
```

### Dual Telemetry Architecture
[Source: Epic 003, Section "Key Architectural Decisions"]

**WebSocket Telemetry (Real-Time):**
- Emitted directly from agent code as events occur
- Latency target: <100ms
- Used for immediate developer debugging visibility
- Transient (lost on disconnect)

**Jaeger Telemetry (Historical):**
- Existing OpenTelemetry instrumentation UNCHANGED
- Batch exported every 5-6 seconds to Jaeger collector
- Used for historical analysis, trace correlation
- Persisted in database for later review

**Both streams active simultaneously** - No conflicts, serve different purposes

### File Locations
[Source: Epic 003, Section "File Organization"]

**New Files:**
- `src/telemetry/event_emitter.py` - TelemetryEmitter class
- `tests/telemetry/test_event_emitter.py` - Unit tests

**Modified Files:**
- `src/app.py` OR `src/ai/agents.py` - Add telemetry hooks in ChatService

**Unchanged:**
- `src/app.py` - OpenTelemetry setup (Jaeger exporter)

### Tech Stack
[Source: Epic 003, Section "Tech Stack"]

- **Python timing:** `import time` (standard library)
- **UUID generation:** `import uuid` (standard library)
- **Datetime:** `from datetime import datetime` (standard library)
- **PydanticAI:** Existing agent framework (no changes)
- **OpenTelemetry:** Existing instrumentation (unchanged)

**No new external dependencies required**

### Testing

#### Test File Locations
- Unit tests: `tests/telemetry/test_event_emitter.py`
- Follow existing pattern: `tests/{module}/test_{file}.py`

#### Testing Standards
[Source: Epic 003, Section "Testing Strategy"]

**Coverage Requirements:**
- TelemetryEmitter: 80%+ (standard project coverage)

**Unit Test Requirements:**
```python
# tests/telemetry/test_event_emitter.py
- Test emit_tool_call() with valid data
- Test emit_tool_result() with duration
- Test emit_openai_call() with token counts
- Test fire-and-forget (doesn't block on errors)
- Test graceful error handling (mock ConnectionManager exception)
- Mock ConnectionManager.send_message() to verify calls
```

**Testing Frameworks:**
- `pytest` - Test runner
- `pytest-asyncio` - Async test support
- `unittest.mock` - Mocking ConnectionManager

**Run Tests:**
```bash
pytest tests/telemetry/ -v
pytest --cov=src/telemetry --cov-report=term-missing
```

#### Integration Testing
[Source: Epic 003, Section "Testing Strategy"]

**Verification Steps:**
1. Start services: `docker compose up -d`
2. Start backend: `uv run uvicorn src:app --port 8000 --reload`
3. Connect WebSocket: `wscat -c "ws://localhost:8000/ws?session_id=test123"`
4. Send message that triggers tool call: `{"type": "message", "session_id": "test123", "content": "What is quintin cole's diagnosis?"}`
5. Observe WebSocket events in real-time (<100ms)
6. Verify Jaeger UI shows same trace (http://localhost:16686, 5-6s delay)

**Expected WebSocket Stream:**
```json
{"type": "tool_call", "session_id": "test123", "tool_call_id": "...", "tool_name": "fetch_patient_data", ...}
{"type": "tool_result", "session_id": "test123", "tool_call_id": "...", "tool_name": "fetch_patient_data", "result": "...", "duration_ms": 234, ...}
{"type": "openai_call", "session_id": "test123", "model": "gpt-4", ...}
{"type": "openai_response", "session_id": "test123", "model": "gpt-4", "prompt_tokens": 150, "completion_tokens": 50, ...}
{"type": "assistant", "session_id": "test123", "content": "Based on the data...", ...}
```

### Technical Constraints
[Source: Epic 003, Section "Key Architectural Decisions"]

1. **Fire-and-forget pattern** - Don't block agent execution for telemetry
2. **Non-blocking** - Use async methods, catch exceptions, log warnings
3. **Dual emission** - Maintain both WebSocket (new) and Jaeger (existing)
4. **Performance** - Telemetry overhead must be <10ms per event
5. **Session correlation** - Use session_id for targeted delivery

### Performance Considerations
- Telemetry emission should add <10ms overhead to agent execution
- Use async/await to prevent blocking
- ConnectionManager.send_message() is fast (in-memory, no I/O)
- Don't serialize large objects in arguments/result (summarize if needed)
- If telemetry fails (disconnected session), agent continues normally

### Security Considerations
[Source: Epic 003, Section "Security Considerations"]

**Current scope:** Development environment only
- No filtering of sensitive data (PHI visible in telemetry)
- Acceptable for localhost development
- Future: Filter PHI from telemetry events before production

### Regression Testing
- All 40+ existing tests must pass
- POST `/patient` endpoint must be unaffected
- Existing OpenTelemetry→Jaeger export must continue working
- Verify with: `pytest tests/` (all tests)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-20 | 1.0 | Initial story creation | Bob (Scrum Master) |

## Dev Agent Record

### Agent Model Used
_To be filled by Dev Agent during implementation_

### Debug Log References
_To be filled by Dev Agent during implementation_

### Completion Notes
_To be filled by Dev Agent during implementation_

### File List
_To be filled by Dev Agent during implementation_

## QA Results
_To be filled by QA Agent after implementation_
