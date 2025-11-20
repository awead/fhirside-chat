# Story 006: Backend WebSocket Infrastructure

**Status:** Draft
**Epic:** 003 - Real-Time WebSocket Chat & Telemetry
**Story Points:** 5
**Estimated Hours:** 8-10 hours

## Story

**As a** backend developer,
**I want** to implement WebSocket infrastructure with ConnectionManager and message protocol models,
**so that** we can support real-time bidirectional communication for chat and telemetry.

## Acceptance Criteria

1. **ConnectionManager Implementation**
   - ConnectionManager class created in `src/websocket/connection_manager.py`
   - Maintains mapping of session_id → WebSocket connection
   - Implements `connect()`, `disconnect()`, and `send_message()` methods
   - Supports broadcasting to specific session or all connections
   - Handles connection cleanup on disconnect
   - 90%+ test coverage (critical infrastructure)

2. **WebSocket Message Protocol Models**
   - All message models defined in `src/models/websocket_messages.py` using Pydantic
   - Client → Server: `UserMessage`
   - Server → Client: `AssistantMessage`, `ToolCallEvent`, `ToolResultEvent`, `OpenAIEvent`, `ErrorMessage`, `ConnectionStatus`
   - All models validated with proper type hints and Literal types
   - Models support JSON serialization/deserialization

3. **Enhanced `/ws` Endpoint**
   - Existing `/ws` endpoint in `src/app.py` enhanced with full message routing
   - Accepts WebSocket connections with session_id query parameter
   - Receives JSON messages and validates using Pydantic models
   - Routes messages based on `type` field (discriminated union)
   - Sends responses as JSON using message protocol models
   - Proper error handling with ErrorMessage responses

4. **Unit Tests**
   - `tests/websocket/test_connection_manager.py` - ConnectionManager methods
   - `tests/websocket/test_websocket_messages.py` - Pydantic validation
   - Test connect/disconnect lifecycle
   - Test message sending to specific session
   - Test concurrent connections
   - Test session isolation (no cross-session data leakage)
   - Achieve 90%+ coverage for ConnectionManager

5. **Integration Checkpoint**
   - Manual testing with wscat or Postman demonstrates:
     - Successful WebSocket connection with session_id
     - JSON message send/receive working
     - Multiple concurrent connections isolated by session
     - Graceful disconnect handling

## Tasks / Subtasks

- [ ] **Task 1: Create WebSocket Message Models** (AC: 2)
  - [ ] Create `src/models/websocket_messages.py`
  - [ ] Define `UserMessage` with type="message", session_id, content
  - [ ] Define `AssistantMessage` with type="assistant", session_id, content, streaming
  - [ ] Define `ToolCallEvent` with type="tool_call", session_id, tool_call_id, tool_name, arguments, timestamp
  - [ ] Define `ToolResultEvent` with type="tool_result", session_id, tool_call_id, tool_name, result, duration_ms, timestamp
  - [ ] Define `OpenAIEvent` with type="openai_call"|"openai_response", session_id, model, tokens, duration_ms, timestamp
  - [ ] Define `ErrorMessage` with type="error", session_id, error
  - [ ] Define `ConnectionStatus` with type="connection", status, session_id
  - [ ] Add proper imports: `from pydantic import BaseModel`, `from typing import Literal, Dict, Any, Optional`, `from datetime import datetime`
  - [ ] Write unit tests in `tests/websocket/test_websocket_messages.py`

- [ ] **Task 2: Implement ConnectionManager** (AC: 1)
  - [ ] Create `src/websocket/` directory with `__init__.py`
  - [ ] Create `src/websocket/connection_manager.py`
  - [ ] Define `ConnectionManager` class with `Dict[str, WebSocket]` for active connections
  - [ ] Implement `async def connect(self, websocket: WebSocket, session_id: str)` - accept connection and store mapping
  - [ ] Implement `async def disconnect(self, session_id: str)` - remove from active connections
  - [ ] Implement `async def send_message(self, session_id: str, message: BaseModel)` - send JSON to specific session
  - [ ] Add error handling for disconnected/invalid sessions
  - [ ] Add logging for connection lifecycle events
  - [ ] Write comprehensive unit tests in `tests/websocket/test_connection_manager.py`

- [ ] **Task 3: Enhance `/ws` Endpoint** (AC: 3)
  - [ ] Import ConnectionManager and message models in `src/app.py`
  - [ ] Create global ConnectionManager instance
  - [ ] Update `/ws` endpoint to use ConnectionManager.connect()
  - [ ] Parse incoming messages as JSON and validate with Pydantic (UserMessage)
  - [ ] Add message routing logic based on `type` field
  - [ ] For "message" type: process with chat_service and respond with AssistantMessage
  - [ ] Add try/except for Pydantic validation errors → send ErrorMessage
  - [ ] Add try/except for WebSocketDisconnect → call ConnectionManager.disconnect()
  - [ ] Send responses as JSON using `.model_dump_json()` or `.json()`
  - [ ] Test manually with wscat: `wscat -c "ws://localhost:8000/ws?session_id=test123"`

- [ ] **Task 4: Create Unit Tests** (AC: 4)
  - [ ] Create `tests/websocket/` directory with `__init__.py`
  - [ ] Write `tests/websocket/test_connection_manager.py`:
    - [ ] Test connect() adds connection to mapping
    - [ ] Test disconnect() removes connection from mapping
    - [ ] Test send_message() sends JSON to correct session
    - [ ] Test send_message() handles missing session gracefully
    - [ ] Test multiple concurrent connections
    - [ ] Test session isolation (messages only go to intended session)
  - [ ] Write `tests/websocket/test_websocket_messages.py`:
    - [ ] Test UserMessage validation (valid and invalid data)
    - [ ] Test AssistantMessage serialization
    - [ ] Test ToolCallEvent with all required fields
    - [ ] Test ToolResultEvent with duration_ms
    - [ ] Test OpenAIEvent with optional token fields
    - [ ] Test ErrorMessage structure
    - [ ] Test ConnectionStatus with Literal status values
  - [ ] Run coverage: `pytest --cov=src/websocket --cov=src/models/websocket_messages --cov-report=term-missing`
  - [ ] Verify 90%+ coverage for ConnectionManager

- [ ] **Task 5: Integration Testing & Checkpoint** (AC: 5)
  - [ ] Start backend: `uv run uvicorn src:app --port 8000 --reload`
  - [ ] Install wscat if needed: `npm install -g wscat`
  - [ ] Test connection: `wscat -c "ws://localhost:8000/ws?session_id=test123"`
  - [ ] Send test message: `{"type": "message", "session_id": "test123", "content": "Hello"}`
  - [ ] Verify JSON response with type="assistant"
  - [ ] Open second wscat with different session_id, verify isolation
  - [ ] Test invalid JSON, verify ErrorMessage response
  - [ ] Test disconnect (Ctrl+C), verify graceful cleanup
  - [ ] Document manual testing results

## Dev Notes

### Previous Story Insights
- Story 005 (Epic 002) completed the telemetry visualization panel with REST polling
- This story begins Epic 003's WebSocket migration to replace REST polling with real-time communication
- Epic 002's telemetry API will be replaced by WebSocket telemetry emission in Story 007

### WebSocket Message Protocol
[Source: Epic 003, Section "WebSocket Message Protocol"]

All messages use discriminated unions with a `type` field for routing:

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

### ConnectionManager Component Specification
[Source: Epic 003, Section "Component Architecture"]

**Purpose:** Manage WebSocket connections by session_id, enabling targeted message delivery

**Class Interface:**
```python
class ConnectionManager:
    active_connections: Dict[str, WebSocket]

    async def connect(self, websocket: WebSocket, session_id: str) -> None
    async def disconnect(self, session_id: str) -> None
    async def send_message(self, session_id: str, message: BaseModel) -> None
```

**Implementation Details:**
- Use `Dict[str, WebSocket]` to map session_id to WebSocket connection
- `connect()` should call `await websocket.accept()` and store mapping
- `disconnect()` should remove from dict (no need to close, already disconnected)
- `send_message()` should serialize message to JSON and send via `websocket.send_text()`
- Handle missing sessions gracefully (log warning, don't raise exception)
- This is critical infrastructure → target 90%+ test coverage

### Current `/ws` Endpoint
[Source: src/app.py, lines 87-97]

Current implementation is minimal:
```python
@app.websocket("/ws")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    session_id = websocket.query_params.get("session_id", "default")
    try:
        while True:
            msg = await websocket.receive_text()
            output = await chat_service.process(session_id, msg)
            await websocket.send_text(output)
    except WebSocketDisconnect:
        return
```

**Enhancements needed:**
- Use ConnectionManager instead of direct `await websocket.accept()`
- Parse incoming text as JSON and validate with Pydantic
- Route messages based on `type` field
- Send responses as JSON using message protocol models
- Add proper error handling with ErrorMessage responses

### File Locations
[Source: Epic 003, Section "File Organization"]

**New Files:**
- `src/models/websocket_messages.py` - Message protocol Pydantic models
- `src/websocket/__init__.py` - Package init
- `src/websocket/connection_manager.py` - ConnectionManager class
- `tests/websocket/__init__.py` - Test package init
- `tests/websocket/test_connection_manager.py` - ConnectionManager unit tests
- `tests/websocket/test_websocket_messages.py` - Message validation tests

**Modified Files:**
- `src/app.py` - Enhanced `/ws` endpoint (lines 87-97)

### Tech Stack
[Source: Epic 003, Section "Tech Stack"]

- **FastAPI:** Native WebSocket support (no new dependencies)
- **Pydantic:** Message validation (already in use)
- **Python typing:** Literal types for discriminated unions
- **pytest:** Unit testing framework (existing)

**No new external dependencies required**

### Testing

#### Test File Locations
- Backend unit tests: `tests/websocket/test_*.py`
- Follow existing project pattern: `tests/{module}/test_{file}.py`

#### Testing Standards
[Source: Epic 003, Section "Testing Strategy"]

**Coverage Requirements:**
- **Overall project:** 80%+ (maintain existing standard)
- **ConnectionManager:** 90%+ (critical infrastructure component)

**Unit Test Requirements:**
```python
# tests/websocket/test_connection_manager.py
- Test connect() - verify connection added to mapping
- Test disconnect() - verify connection removed
- Test send_message() - verify JSON sent to correct session
- Test send_message() with missing session - verify graceful handling
- Test multiple concurrent connections - verify all tracked
- Test session isolation - verify messages only go to intended session

# tests/websocket/test_websocket_messages.py
- Test each message model validation (valid data)
- Test validation failures (missing fields, wrong types)
- Test JSON serialization (.model_dump_json())
- Test discriminated union type field (Literal values)
```

**Testing Frameworks:**
- `pytest` - Test runner (existing)
- `pytest-cov` - Coverage reporting (existing)
- `pytest-asyncio` - Async test support (existing)

**Run Tests:**
```bash
pytest tests/websocket/ -v
pytest --cov=src/websocket --cov=src/models/websocket_messages --cov-report=term-missing
```

#### Integration Testing
[Source: Epic 003, Section "Testing Strategy"]

Manual testing with wscat:
```bash
# Install wscat (WebSocket CLI client)
npm install -g wscat

# Connect to WebSocket
wscat -c "ws://localhost:8000/ws?session_id=test123"

# Send test message (paste this JSON)
{"type": "message", "session_id": "test123", "content": "Hello WebSocket"}

# Expected response (JSON with type="assistant")
{"type": "assistant", "session_id": "test123", "content": "...", "streaming": false}
```

Test scenarios:
1. Valid message → Receives AssistantMessage
2. Invalid JSON → Receives ErrorMessage
3. Multiple connections with different session_ids → Isolated responses
4. Disconnect → Graceful cleanup (no errors in logs)

### Technical Constraints
[Source: Epic 003, Section "Key Architectural Decisions"]

1. **No new dependencies** - Use native FastAPI WebSocket support
2. **Session management** - Use query parameter `?session_id=xxx` (existing pattern)
3. **JSON messaging** - All messages as JSON (not plain text)
4. **Discriminated unions** - Route on `type` field (Pydantic discriminator)
5. **Non-blocking** - ConnectionManager methods should not block agent processing

### Security Considerations
[Source: Epic 003, Section "Security Considerations"]

**Current scope:** Development environment only
- **Protocol:** `ws://` acceptable (localhost)
- **Session validation:** None (accept client-provided session_id)
- **Authentication:** None required for this story
- **Protection:** Pydantic validation prevents malformed messages

**Future (Production - not in this story):**
- Upgrade to `wss://` (TLS)
- JWT authentication
- Session validation
- Connection limits per IP

### Project Structure Notes
Follows existing project structure:
- Models in `src/models/` directory
- New module `src/websocket/` for WebSocket-specific code
- Tests mirror source: `tests/websocket/` for `src/websocket/`
- Use `__init__.py` for package initialization

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
