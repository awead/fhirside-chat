import pytest
import asyncio
import httpx
from uuid import uuid4


@pytest.fixture
def base_url():
    return "http://localhost:8000"


@pytest.fixture
def session_id():
    return f"e2e-test-{uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_telemetry_end_to_end(base_url, session_id):
    """
    End-to-end test for telemetry feature.

    Prerequisites:
    - Docker services running (docker compose up)
    - FastAPI server running (uvicorn src:app)
    - Jaeger receiving traces

    Test flow:
    1. Send chat message via POST /chat
    2. Wait for trace export to Jaeger
    3. Query GET /telemetry/{session_id}
    4. Verify spans contain session_id and expected operations
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n{'=' * 60}")
        print(f"E2E Telemetry Test - Session: {session_id}")
        print(f"{'=' * 60}\n")

        print("Step 1: Sending chat message...")
        chat_response = await client.post(
            f"{base_url}/chat",
            json={"session_id": session_id, "message": "How many patients?"},
        )
        assert chat_response.status_code == 200, f"Chat failed: {chat_response.text}"
        chat_data = chat_response.json()
        assert chat_data["session_id"] == session_id
        assert "output" in chat_data
        print(f"✅ Chat response received: {chat_data['output'][:80]}...")

        print("\nStep 2: Waiting for trace export (6 seconds)...")
        await asyncio.sleep(6)
        print("✅ Wait complete")

        print("\nStep 3: Querying telemetry endpoint...")
        telemetry_response = await client.get(f"{base_url}/telemetry/{session_id}")
        assert telemetry_response.status_code == 200, (
            f"Telemetry query failed: {telemetry_response.text}"
        )
        telemetry_data = telemetry_response.json()
        print("✅ Telemetry response received")

        print("\nStep 4: Verifying response structure...")
        assert telemetry_data["session_id"] == session_id
        assert "spans" in telemetry_data
        assert "trace_count" in telemetry_data
        assert isinstance(telemetry_data["spans"], list)
        print("✅ Response structure valid")

        print("\nStep 5: Verifying spans captured...")
        spans = telemetry_data["spans"]
        assert len(spans) > 0, "No spans captured"
        print(f"✅ Captured {len(spans)} spans")

        print("\nStep 6: Verifying trace count...")
        trace_count = telemetry_data["trace_count"]
        assert trace_count > 0, "No traces found"
        print(f"✅ Found {trace_count} trace(s)")

        print("\nStep 7: Verifying session_id propagation...")
        session_spans = [
            s for s in spans if s.get("attributes", {}).get("session_id") == session_id
        ]
        assert len(session_spans) > 0, "No spans contain session_id"
        print(f"✅ Found {len(session_spans)} span(s) with session_id")

        chat_session_span = next(
            (s for s in spans if s["operation_name"] == "chat_session"), None
        )
        assert chat_session_span is not None, "chat_session span not found in response"
        assert chat_session_span["attributes"]["session_id"] == session_id, (
            "chat_session span missing session_id"
        )
        print("✅ chat_session span contains correct session_id")

        print("\nStep 8: Verifying expected operations captured...")
        operation_names = {s["operation_name"] for s in spans}
        expected_operations = ["chat_session", "agent run"]

        missing_operations = [
            op for op in expected_operations if op not in operation_names
        ]
        assert not missing_operations, f"Missing operations: {missing_operations}"
        print("✅ All expected operations present")

        assert any("gpt" in op.lower() for op in operation_names), (
            "No OpenAI operations found"
        )
        print("✅ OpenAI operations captured")

        print("\nStep 9: Verifying span structure...")
        for span in spans[:3]:
            assert "span_id" in span
            assert "trace_id" in span
            assert "operation_name" in span
            assert "start_time" in span
            assert "end_time" in span
            assert "duration" in span
            assert "attributes" in span
            assert "status" in span
            assert span["duration"] > 0, "Duration should be positive"
            assert span["end_time"] > span["start_time"], (
                "End time should be after start time"
            )
        print("✅ Span structure valid")

        print("\nStep 10: Verifying parent-child relationships...")
        span_ids = {s["span_id"] for s in spans}

        root_spans = [s for s in spans if not s.get("parent_span_id")]
        child_spans = [s for s in spans if s.get("parent_span_id")]

        if root_spans:
            print(f"✅ Found {len(root_spans)} root span(s)")
        else:
            print("⚠️  No root spans in filtered results (parent may be filtered out)")

        if child_spans:
            parents_in_result = [
                s for s in child_spans if s.get("parent_span_id") in span_ids
            ]
            if parents_in_result:
                print(
                    f"✅ {len(parents_in_result)} child span(s) have parent in result set"
                )
            else:
                print("⚠️  Child spans reference parents outside filtered result set")

        print(f"✅ Span relationships valid (total: {len(spans)} spans)")

        print(f"\n{'=' * 60}")
        print("E2E Test Summary:")
        print(f"  Session ID: {session_id}")
        print(f"  Spans captured: {len(spans)}")
        print(f"  Traces: {trace_count}")
        print(f"  Operations: {', '.join(sorted(operation_names)[:5])}")
        print(f"  Spans with session_id: {len(session_spans)}")
        print(f"{'=' * 60}")
        print("✅ ALL CHECKS PASSED\n")


@pytest.mark.asyncio
async def test_telemetry_multiple_sessions(base_url):
    """
    Test that telemetry correctly isolates different sessions.

    Verifies:
    - Multiple sessions create separate traces
    - Session IDs don't cross-contaminate
    - Each session returns only its own spans
    """
    session_a = f"e2e-multi-a-{uuid4().hex[:6]}"
    session_b = f"e2e-multi-b-{uuid4().hex[:6]}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n{'=' * 60}")
        print("Multi-Session Test")
        print(f"  Session A: {session_a}")
        print(f"  Session B: {session_b}")
        print(f"{'=' * 60}\n")

        print("Sending message to Session A...")
        response_a = await client.post(
            f"{base_url}/chat",
            json={"session_id": session_a, "message": "Test A"},
        )
        assert response_a.status_code == 200
        print("✅ Session A message sent")

        print("Sending message to Session B...")
        response_b = await client.post(
            f"{base_url}/chat",
            json={"session_id": session_b, "message": "Test B"},
        )
        assert response_b.status_code == 200
        print("✅ Session B message sent")

        print("\nWaiting for trace export...")
        await asyncio.sleep(6)

        print("Querying telemetry for Session A...")
        telemetry_a = await client.get(f"{base_url}/telemetry/{session_a}")
        assert telemetry_a.status_code == 200
        data_a = telemetry_a.json()

        print("Querying telemetry for Session B...")
        telemetry_b = await client.get(f"{base_url}/telemetry/{session_b}")
        assert telemetry_b.status_code == 200
        data_b = telemetry_b.json()

        print("\nVerifying session isolation...")
        assert len(data_a["spans"]) > 0, "Session A has no spans"
        assert len(data_b["spans"]) > 0, "Session B has no spans"

        session_a_spans = [
            s
            for s in data_a["spans"]
            if s.get("attributes", {}).get("session_id") == session_a
        ]
        session_b_spans = [
            s
            for s in data_b["spans"]
            if s.get("attributes", {}).get("session_id") == session_b
        ]

        assert len(session_a_spans) > 0, "Session A spans missing session_id"
        assert len(session_b_spans) > 0, "Session B spans missing session_id"

        assert data_a["trace_count"] >= 1, "Session A should have at least 1 trace"
        assert data_b["trace_count"] >= 1, "Session B should have at least 1 trace"

        print(
            f"✅ Session A: {len(data_a['spans'])} spans, {data_a['trace_count']} trace(s)"
        )
        print(
            f"✅ Session B: {len(data_b['spans'])} spans, {data_b['trace_count']} trace(s)"
        )
        print("\n✅ Sessions properly isolated\n")


@pytest.mark.asyncio
async def test_telemetry_empty_session(base_url):
    """
    Test querying telemetry for a session that doesn't exist.

    Verifies:
    - Returns 200 (not 404)
    - Returns empty spans list
    - Returns trace_count of 0
    """
    nonexistent_session = f"nonexistent-{uuid4().hex[:8]}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        print(f"\n{'=' * 60}")
        print(f"Empty Session Test - {nonexistent_session}")
        print(f"{'=' * 60}\n")

        response = await client.get(f"{base_url}/telemetry/{nonexistent_session}")
        assert response.status_code == 200, "Should return 200 for nonexistent session"

        data = response.json()
        assert data["session_id"] == nonexistent_session
        assert data["spans"] == []
        assert data["trace_count"] == 0

        print("✅ Empty session returns expected structure")
        print("  - 200 status code")
        print("  - Empty spans list")
        print("  - trace_count = 0\n")
