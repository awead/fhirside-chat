# Story 002: Backend Telemetry API Endpoint - Completion Summary

**Date:** 2025-11-20
**Status:** ✅ Complete
**Story ID:** STORY-002
**Total Duration:** Single session development + E2E testing

---

## Executive Summary

Successfully implemented a REST API endpoint that exposes OpenTelemetry trace data for chat sessions. The telemetry endpoint enables frontend developers to display real-time observability data showing OpenAI API calls, agent operations, and MCP queries. The feature includes comprehensive unit, integration, and end-to-end testing.

**Key Achievement:** Fully functional telemetry pipeline from chat interaction to trace visualization, with automated E2E tests ensuring long-term reliability.

---

## What Was Built

### 1. Core Components

#### Telemetry Data Models (`src/models/telemetry.py`)
- `SpanAttributes` - OpenAI and MCP attribute fields with Pydantic aliases for dotted keys
- `SpanData` - Complete span metadata (timing, hierarchy, attributes, status)
- `TelemetryResponse` - API response wrapper with session_id, spans, and trace_count

**Features:**
- Field validation with Pydantic
- JSON serialization with camelCase for frontend
- OpenAPI schema examples for documentation
- Null-safe attribute handling

#### Jaeger Query Client (`src/telemetry/jaeger_client.py`)
- Async HTTP client querying Jaeger API at `http://localhost:16686/api/traces`
- Tag-based filtering by `session_id`
- Span relevance filtering (OpenAI, MCP, agent operations)
- Parent-child relationship parsing
- Graceful error handling with logging

**Features:**
- 5-second timeout for Jaeger queries
- Empty list return on errors (no 500s)
- Structured logging for debugging
- Extensible span filtering

#### Telemetry API Endpoint (`src/app.py`)
```python
GET /telemetry/{session_id}
```

**Response Example:**
```json
{
  "session_id": "abc-123",
  "spans": [
    {
      "span_id": "abc123",
      "trace_id": "xyz789",
      "operation_name": "chat gpt-5-mini",
      "start_time": 1700000000000000000,
      "end_time": 1700000001000000000,
      "duration": 1000000000,
      "attributes": {
        "session_id": "abc-123"
      },
      "status": "OK"
    }
  ],
  "trace_count": 1
}
```

**Features:**
- Returns 200 even for nonexistent sessions (empty spans)
- Calculates unique trace count
- CORS enabled for localhost:3000, localhost:5173
- Comprehensive error handling and logging

#### Session ID Instrumentation
- Created `chat_session` wrapper span in `ChatService.process()`
- Sets `session_id` attribute that propagates through trace context
- Links FastAPI HTTP spans with PydanticAI agent spans
- Minimal code change (wrapper span around agent execution)

#### FastAPI Instrumentation
- Added `opentelemetry-instrumentation-fastapi` package
- Automatic span creation for all HTTP requests
- Integration with existing OpenTelemetry setup
- Module-level tracer initialization

### 2. Testing Infrastructure

#### Unit Tests (24 tests)
- `tests/models/test_telemetry.py` - 8 model validation tests
- `tests/telemetry/test_jaeger_client.py` - 12 Jaeger client tests
- `tests/test_telemetry_endpoint.py` - 4 endpoint integration tests

#### End-to-End Tests (3 tests)
- `tests/e2e/test_telemetry_e2e.py` - Comprehensive E2E test suite
  - `test_telemetry_end_to_end` - Full workflow with 10 verification steps
  - `test_telemetry_multiple_sessions` - Session isolation verification
  - `test_telemetry_empty_session` - Edge case handling

**E2E Test Coverage:**
- Chat message sending
- Trace export timing (6-second wait)
- Telemetry query and response validation
- Session ID propagation verification
- Span structure and relationships
- Multi-session isolation
- Graceful error handling

#### Test Documentation
- `tests/e2e/README.md` - Complete E2E testing guide
  - Prerequisites and setup instructions
  - Running tests individually and as suite
  - Troubleshooting common issues
  - CI/CD integration examples
  - Development tips

### 3. Documentation

#### README Updates
- Telemetry endpoint usage examples
- Example curl commands
- JSON response structure
- **Security warnings** (prominent, repeated)
- CORS configuration notes
- API documentation links (Swagger UI, ReDoc)

#### Story Documentation
- Complete task breakdown with subtasks
- Change log with timestamps
- File list (new and modified)
- Completion notes with key decisions
- E2E testing learnings

---

## Technical Decisions

### Architecture Choices

**1. Jaeger Query API vs Direct Database**
- **Decision:** Use Jaeger Query API
- **Rationale:**
  - Official API with stable interface
  - No direct database coupling
  - Jaeger handles trace aggregation
  - Future-proof for Jaeger upgrades

**2. Session ID Propagation via Wrapper Span**
- **Decision:** Create explicit `chat_session` span with session_id attribute
- **Rationale:**
  - PydanticAI and FastAPI create separate traces
  - Wrapper span provides single correlation point
  - Minimal code change (single context manager)
  - Session ID visible in Jaeger UI

**3. Span Filtering Strategy**
- **Decision:** Whitelist-based filtering for relevant operations
- **Rationale:**
  - Frontend doesn't need internal FastAPI spans
  - Reduce payload size
  - Focus on AI/MCP operations
  - Extensible for future operation types

**4. Error Handling: Empty List vs 404**
- **Decision:** Return 200 with empty spans for nonexistent sessions
- **Rationale:**
  - Consistent with trace export timing (not instant)
  - Frontend can handle empty state gracefully
  - No difference between "not yet exported" and "never existed"
  - Simpler client error handling

### Implementation Patterns

**Async/Await Throughout**
- All I/O operations use async (httpx, FastAPI)
- Consistent with existing codebase
- Enables high concurrency

**Pydantic for Data Validation**
- Type safety at API boundaries
- Automatic OpenAPI schema generation
- Follows existing pattern (clinical_history.py)

**Structured Logging**
- Contextual log fields (session_id, span_count, errors)
- Separate logger for telemetry (`telemetry_logger`)
- Enables log aggregation and debugging

---

## Issues Discovered & Fixed

### Issue #1: FastAPI Not Instrumented
**Problem:** FastAPI endpoints weren't creating OpenTelemetry spans

**Symptoms:**
- No HTTP request spans in Jaeger
- Session ID context not available to agent code

**Root Cause:**
- OpenTelemetry configured but FastAPI not instrumented
- `instrumentation()` only set up for PydanticAI

**Fix:**
```python
# Added package
opentelemetry-instrumentation-fastapi>=0.59b0

# Added instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
app = create_app()
FastAPIInstrumentor.instrument_app(app)
```

**Impact:** Now HTTP spans link to agent spans in single trace

### Issue #2: Session ID Not in Spans
**Problem:** `session_id` attribute not appearing in exported spans

**Symptoms:**
- Jaeger query by `session_id` tag returned no results
- `trace.get_current_span().set_attribute()` not working

**Root Cause:**
- No active span context when `ChatService.process()` called
- PydanticAI creates separate trace context

**Fix:**
```python
# Create explicit wrapper span
with tracer.start_as_current_span(
    "chat_session",
    attributes={"session_id": session_id}
):
    # Agent execution here
```

**Impact:** Session ID now propagates through entire trace

### Issue #3: Span Filter Too Restrictive
**Problem:** Telemetry endpoint returned empty spans despite Jaeger having data

**Symptoms:**
- Manual Jaeger UI showed traces
- API endpoint returned empty list

**Root Cause:**
- Filter only accepted `openai.*` and `mcp.*` prefixes
- PydanticAI operations use different names: `chat gpt-5-mini`, `agent run`

**Fix:**
```python
# Extended filter
def _is_relevant_span(jaeger_span: dict) -> bool:
    operation_name = jaeger_span.get("operationName", "")
    return (
        operation_name.startswith("openai.") or
        operation_name.startswith("mcp.") or
        operation_name.startswith("chat ") or
        operation_name.startswith("agent ") or
        "gpt" in operation_name.lower() or
        operation_name == "chat_session" or
        operation_name in ["running tool", "running tools"]
    )
```

**Impact:** All relevant AI operations now captured

### Issue #4: Tracer Not Initialized
**Problem:** Wrapper span not appearing in Jaeger

**Symptoms:**
- `chat_session` operation not in Jaeger operations list
- No spans created by wrapper

**Root Cause:**
- `instrumentation()` never called at app startup
- TracerProvider not configured

**Fix:**
```python
# Add to module level
from src.ai.telemetry import instrumentation
instrumentation()
```

**Impact:** Tracer properly configured before any span creation

---

## Test Results

### Final Test Count: 40 Tests Passing ✅

**Unit Tests:** 37 passing
- AI agents: 2 tests
- AI telemetry: 1 test
- Clinical history models: 4 tests
- Telemetry models: 8 tests
- Jaeger client: 12 tests
- Main app endpoints: 6 tests
- Telemetry endpoint: 4 tests

**E2E Tests:** 3 passing (~29 seconds)
- Full workflow test: 11.82s
- Multi-session test: 15.21s
- Empty session test: 2.19s

**Code Quality:**
- Ruff linting: ✅ Passing
- Ruff formatting: ✅ Applied
- Type hints: ✅ Complete
- No violations: ✅ Clean

---

## Security Considerations

### Current Configuration (Development Only)

**CORS Enabled For:**
- `http://localhost:3000` (typical React dev server)
- `http://localhost:5173` (Vite dev server)

**Credentials:** `allow_credentials=True`

**Methods:** GET, POST, OPTIONS

**Headers:** All (`*`)

### Production Requirements ⚠️

**This endpoint exposes sensitive data:**
1. OpenAI prompts and completions
2. MCP FHIR queries and responses
3. Potentially PHI (Protected Health Information)
4. Session correlation data

**Before production deployment:**
- [ ] Implement authentication (JWT, OAuth2)
- [ ] Implement authorization (role-based access)
- [ ] Filter PHI from trace attributes
- [ ] Restrict CORS to production domains
- [ ] Add rate limiting
- [ ] Consider data retention policies
- [ ] Audit log access to telemetry data

---

## Dependencies Added

```toml
# pyproject.toml
[project.dependencies]
httpx = ">=0.28.1"
opentelemetry-instrumentation-fastapi = ">=0.59b0"
```

**Why httpx:**
- Async HTTP client for Jaeger API
- Modern, well-maintained
- Compatible with FastAPI ecosystem

**Why opentelemetry-instrumentation-fastapi:**
- Automatic span creation for HTTP requests
- Official OpenTelemetry instrumentation
- Integrates with existing OTLP exporter

---

## Files Created

```
src/
  models/
    telemetry.py                    # Data models (149 lines)
  telemetry/
    __init__.py                     # Module init
    jaeger_client.py                # Jaeger API client (170 lines)

tests/
  models/
    test_telemetry.py               # Model tests (145 lines)
  telemetry/
    __init__.py                     # Module init
    test_jaeger_client.py           # Client tests (224 lines)
  test_telemetry_endpoint.py        # Endpoint tests (144 lines)
  e2e/
    __init__.py                     # Module init
    test_telemetry_e2e.py           # E2E tests (268 lines)
    README.md                       # E2E test guide
```

## Files Modified

```
src/app.py                          # +45 lines (instrumentation + endpoint)
pyproject.toml                      # +2 dependencies
README.md                           # +52 lines (telemetry docs)
docs/stories/
  story-002-telemetry-api-endpoint.md  # Complete documentation
```

**Total Lines of Code:** ~1,197 new lines
**Total Lines of Tests:** ~781 test lines
**Test Coverage Ratio:** ~65% test code

---

## Running the Feature

### Prerequisites

```bash
# Start Docker services (Aidbox, PostgreSQL, Jaeger)
docker compose up -d

# Start FastAPI server
uv run uvicorn src:app --host 0.0.0.0 --port 8000 --reload
```

### Usage Example

```bash
# 1. Send a chat message
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "test-session-123",
    "message": "How many patients are in the system?"
  }'

# Response:
# {"session_id":"test-session-123","output":"There are 113 patients..."}

# 2. Wait for trace export (5-6 seconds)
sleep 6

# 3. Query telemetry
curl http://localhost:8000/telemetry/test-session-123 | jq

# Response: JSON with spans array, trace_count, session_id
```

### Verify in Jaeger UI

```bash
open http://localhost:16686

# Search for:
# - Service: fhir-chat-agent
# - Tags: session_id:test-session-123
# - Operations: chat_session, agent run, chat gpt-5-mini
```

---

## Next Steps / Handoff Notes

### For Frontend Developers (Story 003-005)

**The telemetry endpoint is ready to use:**

1. **Endpoint:** `GET /telemetry/{session_id}`
2. **CORS:** Enabled for localhost:3000 and localhost:5173
3. **Response:** Typed models available in story docs
4. **Timing:** Wait 5-6 seconds after chat for traces to export

**Example Integration:**
```typescript
// TypeScript example for Story 003
const response = await fetch(
  `http://localhost:8000/telemetry/${sessionId}`
);
const data = await response.json();
// data.spans array contains telemetry data
```

### For Backend Developers

**Potential Enhancements:**
1. Add WebSocket support for real-time trace updates
2. Implement trace filtering by time range
3. Add pagination for sessions with many spans
4. Cache Jaeger responses (with short TTL)
5. Add metrics (query latency, span counts)
6. Implement trace sampling controls

**Known Limitations:**
1. No authentication (development only)
2. No rate limiting
3. No data filtering (exposes all attributes)
4. Synchronous Jaeger queries (could be background task)
5. No trace data persistence (relies on Jaeger retention)

### For DevOps / SRE

**Production Deployment Checklist:**
- [ ] Configure Jaeger retention policy
- [ ] Set up authentication/authorization
- [ ] Add rate limiting middleware
- [ ] Configure CORS for production domains
- [ ] Set up monitoring/alerting for endpoint
- [ ] Review trace data for PHI exposure
- [ ] Configure log aggregation
- [ ] Set resource limits (memory, CPU)
- [ ] Test with production-scale trace volumes

---

## Lessons Learned

### What Went Well ✅

1. **Pydantic Models** - Type safety caught issues early
2. **Async Patterns** - Performance remained high
3. **E2E Testing** - Discovered 4 critical issues before production
4. **Structured Logging** - Easy debugging with contextual logs
5. **Incremental Development** - Task-by-task approach prevented scope creep

### What Could Be Improved 🔄

1. **Initial E2E Testing** - Should have run E2E tests earlier
2. **Instrumentation Setup** - OpenTelemetry setup was fragmented
3. **Documentation** - Could have documented integration points upfront
4. **Trace Export Timing** - 5-6 second delay surprising; needs documentation

### Best Practices Established 📋

1. **E2E tests are mandatory** for integration features
2. **Test with real services** when possible (not just mocks)
3. **Document security implications** explicitly and early
4. **Use wrapper spans** for cross-library context propagation
5. **Filter telemetry data** at API boundary (don't expose everything)

---

## Success Metrics

✅ **All acceptance criteria met**
✅ **40/40 tests passing**
✅ **Zero regressions in existing functionality**
✅ **Comprehensive E2E test coverage**
✅ **Documentation complete and accurate**
✅ **Ready for frontend integration**

**Feature is production-ready pending authentication/authorization implementation.**

---

## References

- [Story 002 Full Documentation](./story-002-telemetry-api-endpoint.md)
- [E2E Test Guide](../../tests/e2e/README.md)
- [Jaeger Query API Docs](https://www.jaegertracing.io/docs/latest/apis/#query-api)
- [OpenTelemetry Python Docs](https://opentelemetry.io/docs/languages/python/)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-20
**Prepared By:** Development Team
**Reviewed By:** [Pending]
