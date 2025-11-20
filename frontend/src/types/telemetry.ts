export interface SpanAttributes {
  'openai.prompt'?: string;
  'openai.completion'?: string;
  'openai.model'?: string;
  'openai.token_count'?: number;
  'mcp.query'?: string;
  'mcp.resource_type'?: string;
  'mcp.response'?: string;
  session_id?: string;
  [key: string]: string | number | undefined;
}

export interface SpanData {
  span_id: string;
  trace_id: string;
  parent_span_id?: string;
  operation_name: string;
  start_time: number;
  end_time: number;
  duration: number;
  attributes: SpanAttributes;
  status: 'OK' | 'ERROR';
  error_message?: string;
}

export interface TelemetryResponse {
  session_id: string;
  spans: SpanData[];
  trace_count: number;
}

export type SpanType = 'openai' | 'mcp' | 'unknown';

export function getSpanType(operationName: string): SpanType {
  const lowerName = operationName.toLowerCase();
  if (lowerName.startsWith('openai.') || lowerName.includes('openai') || lowerName.includes('gpt')) {
    return 'openai';
  }
  if (lowerName.startsWith('mcp.') || lowerName.includes('mcp') || lowerName.includes('aidbox') || lowerName.includes('fhir')) {
    return 'mcp';
  }
  return 'unknown';
}

export function formatDuration(durationNs: number): string {
  const ms = durationNs / 1_000_000;
  if (ms < 1000) {
    return `${Math.round(ms)}ms`;
  }
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatTimestamp(timestampNs: number): string {
  const date = new Date(timestampNs / 1_000_000);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3,
  });
}
