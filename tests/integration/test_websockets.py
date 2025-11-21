import json

from fastapi.testclient import TestClient

from src.app import app


def test_websocket_valid_message():
    client = TestClient(app)

    with client.websocket_connect("/ws?session_id=test-123") as websocket:
        test_message = {
            "type": "message",
            "session_id": "test-123",
            "content": "Hello WebSocket",
        }

        websocket.send_text(json.dumps(test_message))

        messages = []
        for _ in range(3):
            response = websocket.receive_text()
            messages.append(json.loads(response))

        openai_call = next(m for m in messages if m["type"] == "openai_call")
        openai_response = next(m for m in messages if m["type"] == "openai_response")
        assistant_msg = next(m for m in messages if m["type"] == "assistant")

        assert openai_call["session_id"] == "test-123"
        assert openai_response["session_id"] == "test-123"
        assert "duration_ms" in openai_response

        assert assistant_msg["session_id"] == "test-123"
        assert "content" in assistant_msg
        assert assistant_msg["streaming"] is False

        print("\n✓ Valid message test passed (with telemetry)")
        print(f"  Request: {test_message}")
        print("  Telemetry events: openai_call, openai_response")
        print(f"  Assistant response: {assistant_msg}")


def test_websocket_invalid_json():
    client = TestClient(app)

    with client.websocket_connect("/ws?session_id=test-456") as websocket:
        websocket.send_text("not valid json")
        response = websocket.receive_text()
        response_data = json.loads(response)

        assert response_data["type"] == "error"
        assert response_data["session_id"] == "test-456"
        assert "Invalid message format" in response_data["error"]

        print("\n✓ Invalid JSON test passed")
        print(f"  Response: {response_data}")


def test_websocket_invalid_message_type():
    client = TestClient(app)

    with client.websocket_connect("/ws?session_id=test-789") as websocket:
        test_message = {"type": "invalid_type", "session_id": "test-789"}

        websocket.send_text(json.dumps(test_message))
        response = websocket.receive_text()
        response_data = json.loads(response)

        assert response_data["type"] == "error"
        assert response_data["session_id"] == "test-789"

        print("\n✓ Invalid message type test passed")
        print(f"  Response: {response_data}")


def test_websocket_multiple_sessions():
    client = TestClient(app)

    with client.websocket_connect("/ws?session_id=session-A") as ws_a:
        with client.websocket_connect("/ws?session_id=session-B") as ws_b:
            msg_a = {
                "type": "message",
                "session_id": "session-A",
                "content": "Message A",
            }
            msg_b = {
                "type": "message",
                "session_id": "session-B",
                "content": "Message B",
            }

            ws_a.send_text(json.dumps(msg_a))
            ws_b.send_text(json.dumps(msg_b))

            response_a = json.loads(ws_a.receive_text())
            response_b = json.loads(ws_b.receive_text())

            assert response_a["session_id"] == "session-A"
            assert response_b["session_id"] == "session-B"

            print("\n✓ Multiple sessions test passed (sessions isolated)")
            print(f"  Session A first event: {response_a['type']}")
            print(f"  Session B first event: {response_b['type']}")


if __name__ == "__main__":
    print("=" * 60)
    print("WebSocket Integration Tests")
    print("=" * 60)

    test_websocket_valid_message()
    test_websocket_invalid_json()
    test_websocket_invalid_message_type()
    test_websocket_multiple_sessions()

    print("\n" + "=" * 60)
    print("✓ All integration tests passed!")
    print("=" * 60)
