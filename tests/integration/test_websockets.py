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
        response = websocket.receive_text()
        response_data = json.loads(response)

        assert response_data["type"] == "assistant"
        assert response_data["session_id"] == "test-123"
        assert "content" in response_data
        assert response_data["streaming"] is False

        print("\n✓ Valid message test passed")
        print(f"  Request: {test_message}")
        print(f"  Response: {response_data}")


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

            print("\n✓ Multiple sessions test passed")
            print(f"  Session A isolated: {response_a['session_id']}")
            print(f"  Session B isolated: {response_b['session_id']}")


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
