export type UserMessage = {
  type: "message";
  session_id: string;
  content: string;
};

export type AssistantMessage = {
  type: "assistant";
  session_id: string;
  content: string;
  streaming?: boolean;
};

export type ToolCallEvent = {
  type: "tool_call";
  session_id: string;
  tool_call_id: string;
  tool_name: string;
  arguments: Record<string, unknown>;
  timestamp: string;
};

export type ToolResultEvent = {
  type: "tool_result";
  session_id: string;
  tool_call_id: string;
  tool_name: string;
  result: string;
  duration_ms: number;
  timestamp: string;
};

export type OpenAIEvent = {
  type: "openai_call" | "openai_response";
  session_id: string;
  model: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  duration_ms?: number;
  timestamp: string;
};

export type ErrorMessage = {
  type: "error";
  session_id: string;
  error: string;
};

export type ConnectionStatus = {
  type: "connection";
  status: "connected" | "disconnected" | "reconnecting";
  session_id: string;
};

export type TelemetryEvent = ToolCallEvent | ToolResultEvent | OpenAIEvent;

export type WebSocketMessage =
  | UserMessage
  | AssistantMessage
  | ToolCallEvent
  | ToolResultEvent
  | OpenAIEvent
  | ErrorMessage
  | ConnectionStatus;
