import type { TelemetryResponse } from '../types/telemetry';

export class TelemetryApiError extends Error {
  status: number;
  statusText: string;

  constructor(message: string, status: number, statusText: string) {
    super(message);
    this.name = 'TelemetryApiError';
    this.status = status;
    this.statusText = statusText;
  }
}

export async function fetchTelemetry(sessionId: string): Promise<TelemetryResponse> {
  try {
    const response = await fetch(`/telemetry/${encodeURIComponent(sessionId)}`);

    if (!response.ok) {
      throw new TelemetryApiError(
        `Failed to fetch telemetry: ${response.status} ${response.statusText}`,
        response.status,
        response.statusText
      );
    }

    const data: TelemetryResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof TelemetryApiError) {
      throw error;
    }

    if (error instanceof TypeError) {
      throw new TelemetryApiError(
        'Network error: Unable to connect to backend',
        0,
        'Network Error'
      );
    }

    throw new TelemetryApiError(
      'Unknown error fetching telemetry',
      500,
      'Internal Error'
    );
  }
}
