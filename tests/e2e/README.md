# End-to-End Tests

This directory contains end-to-end (E2E) integration tests that verify the complete telemetry feature workflow with real services.

## Prerequisites

Before running E2E tests, ensure all services are running:

### 1. Start Docker Services

```bash
docker compose up -d
```

This starts:
- **Aidbox** (FHIR server) on port 8080
- **PostgreSQL** (Aidbox database) on port 5432
- **Jaeger** (tracing backend) on ports 4317, 4318, 16686

### 2. Start FastAPI Server

```bash
uv run uvicorn src:app --host 0.0.0.0 --port 8000
```

The API should be accessible at `http://localhost:8000`

### 3. Verify Services

```bash
# Check Docker services
docker compose ps

# Check Aidbox health
curl http://localhost:8080/health

# Check Jaeger UI
open http://localhost:16686

# Check FastAPI
curl http://localhost:8000/docs
```

## Running E2E Tests

### Run All E2E Tests

```bash
uv run pytest tests/e2e/ -v
```

### Run Specific Test

```bash
# Run main telemetry E2E test
uv run pytest tests/e2e/test_telemetry_e2e.py::test_telemetry_end_to_end -v

# Run multi-session test
uv run pytest tests/e2e/test_telemetry_e2e.py::test_telemetry_multiple_sessions -v

# Run empty session test
uv run pytest tests/e2e/test_telemetry_e2e.py::test_telemetry_empty_session -v
```

### Run with Detailed Output

```bash
uv run pytest tests/e2e/ -v -s
```

The `-s` flag shows print statements for detailed test progress.

## Test Coverage

### `test_telemetry_end_to_end`

**Purpose:** Verifies complete telemetry workflow from chat message to trace retrieval.

**Steps:**
1. Send chat message via POST /chat
2. Wait for trace export (6 seconds)
3. Query GET /telemetry/{session_id}
4. Verify response structure
5. Verify spans captured
6. Verify session_id propagation
7. Verify expected operations (chat_session, agent run, OpenAI)
8. Verify span structure (timing, attributes, etc.)
9. Verify parent-child span relationships
10. Print comprehensive test summary

**Expected Results:**
- ✅ Chat message processed successfully
- ✅ Multiple spans captured (typically 4-8)
- ✅ `chat_session` span contains session_id
- ✅ Agent and OpenAI operations present
- ✅ Valid parent-child relationships

### `test_telemetry_multiple_sessions`

**Purpose:** Ensures telemetry correctly isolates different chat sessions.

**Steps:**
1. Send messages to two different sessions
2. Wait for trace export
3. Query telemetry for each session
4. Verify each session returns only its own spans

**Expected Results:**
- ✅ Each session has separate spans
- ✅ No cross-contamination between sessions
- ✅ Each session has its own trace(s)

### `test_telemetry_empty_session`

**Purpose:** Tests graceful handling of nonexistent sessions.

**Steps:**
1. Query telemetry for a session ID that was never used
2. Verify response format

**Expected Results:**
- ✅ Returns 200 OK (not 404)
- ✅ Returns empty spans list
- ✅ Returns trace_count = 0

## Troubleshooting

### Tests Fail: "Connection refused"

**Cause:** Services not running

**Solution:**
```bash
# Start Docker services
docker compose up -d

# Start FastAPI server
uv run uvicorn src:app --host 0.0.0.0 --port 8000
```

### Tests Fail: "No spans captured"

**Cause:** Traces not exported to Jaeger yet

**Solution:**
- Wait longer (traces export asynchronously)
- Check Jaeger UI at http://localhost:16686
- Verify OpenTelemetry instrumentation is working
- Check FastAPI server logs for errors

### Tests Fail: "No spans contain session_id"

**Cause:** Session ID not being propagated to spans

**Solution:**
- Verify `ChatService.process()` creates `chat_session` span
- Verify FastAPI instrumentation is active
- Check that `instrumentation()` is called at app startup
- Verify `opentelemetry-instrumentation-fastapi` is installed

### Jaeger Not Receiving Traces

**Solution:**
```bash
# Check Jaeger is running
docker compose ps | grep jaeger

# Check Jaeger logs
docker compose logs jaeger

# Verify OTLP endpoint
curl http://localhost:4318/v1/traces

# Check FastAPI server is exporting
# Look for "INFO:httpx" logs for OTLP exports in server output
```

## CI/CD Integration

For CI/CD pipelines, use Docker Compose to run services:

```yaml
# Example GitHub Actions workflow
- name: Start services
  run: docker compose up -d

- name: Wait for services
  run: |
    timeout 30 bash -c 'until curl -f http://localhost:8080/health; do sleep 1; done'

- name: Start FastAPI
  run: |
    uv run uvicorn src:app --host 0.0.0.0 --port 8000 &
    sleep 5

- name: Run E2E tests
  run: uv run pytest tests/e2e/ -v

- name: Cleanup
  run: docker compose down
```

## Development Tips

### Add New E2E Test

1. Create test function with `@pytest.mark.asyncio` decorator
2. Use `httpx.AsyncClient` for HTTP requests
3. Add `await asyncio.sleep(6)` after operations that create traces
4. Assert on response structure and data
5. Include descriptive print statements for debugging

### Debug Failing Tests

```bash
# Run with verbose output and show prints
uv run pytest tests/e2e/ -vv -s --tb=short

# Run single test with full traceback
uv run pytest tests/e2e/test_telemetry_e2e.py::test_telemetry_end_to_end -vv -s

# Check Jaeger for traces manually
open http://localhost:16686
# Look for service: fhir-chat-agent
# Search by tag: session_id:{your-session-id}
```

### Timing Considerations

- **Trace export delay:** 5-6 seconds (BatchSpanProcessor default)
- **Test timeout:** 30 seconds per HTTP request
- **Total test duration:** ~10-15 seconds per test

Adjust `asyncio.sleep()` timing if traces aren't appearing in tests.

## Notes

- E2E tests require real services (not mocked)
- Tests use unique session IDs to avoid conflicts
- Tests are safe to run in parallel (isolated sessions)
- Cleanup is automatic (no persistent state changes)
- Tests verify both happy path and edge cases
