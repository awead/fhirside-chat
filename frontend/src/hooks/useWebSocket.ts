import { useCallback, useEffect, useRef, useState } from "react";
import type {
  AssistantMessage,
  TelemetryEvent,
  UserMessage,
  WebSocketMessage,
} from "@/types/websocket";

interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (content: string) => void;
  messages: AssistantMessage[];
  telemetryEvents: TelemetryEvent[];
  error: string | null;
}

const MAX_RETRIES = 10;
const MAX_DELAY = 30000;
const INITIAL_DELAY = 1000;

export function useWebSocket(sessionId: string): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [telemetryEvents, setTelemetryEvents] = useState<TelemetryEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const retryCountRef = useRef(0);
  const retryDelayRef = useRef(INITIAL_DELAY);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const connectRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return;
      }

      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws?session_id=${sessionId}`;

      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
          setError(null);
          retryCountRef.current = 0;
          retryDelayRef.current = INITIAL_DELAY;
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data) as WebSocketMessage;

            switch (message.type) {
              case "assistant":
                setMessages((prev) => [...prev, message]);
                break;
              case "tool_call":
              case "tool_result":
              case "openai_call":
              case "openai_response":
                setTelemetryEvents((prev) => [...prev, message]);
                break;
              case "error":
                setError(message.error);
                break;
              case "connection":
                break;
            }
          } catch (err) {
            console.warn("Failed to parse WebSocket message:", err);
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          wsRef.current = null;

          if (retryCountRef.current < MAX_RETRIES) {
            retryCountRef.current++;
            const delay = Math.min(retryDelayRef.current, MAX_DELAY);
            retryDelayRef.current = delay * 2;

            reconnectTimeoutRef.current = window.setTimeout(() => {
              if (connectRef.current) {
                connectRef.current();
              }
            }, delay);
          } else {
            setError("Max reconnection attempts reached");
          }
        };

        ws.onerror = (event) => {
          console.error("WebSocket error:", event);
        };
      } catch (err) {
        console.error("Failed to create WebSocket:", err);
        setError("Failed to establish connection");
      }
    };

    connectRef.current = connect;
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [sessionId]);

  const sendMessage = useCallback(
    (content: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        const message: UserMessage = {
          type: "message",
          session_id: sessionId,
          content,
        };
        wsRef.current.send(JSON.stringify(message));
      } else {
        console.warn("WebSocket is not connected");
      }
    },
    [sessionId]
  );

  return {
    isConnected,
    sendMessage,
    messages,
    telemetryEvents,
    error,
  };
}
