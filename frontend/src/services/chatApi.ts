import type { ChatRequest, ChatResponse } from '../types/chat';

export class ChatApiError extends Error {
  status?: number;
  statusText?: string;

  constructor(message: string, status?: number, statusText?: string) {
    super(message);
    this.name = 'ChatApiError';
    this.status = status;
    this.statusText = statusText;
  }
}

export async function sendMessage(
  sessionId: string,
  message: string
): Promise<string> {
  try {
    const request: ChatRequest = {
      session_id: sessionId,
      message,
    };

    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new ChatApiError(
        `API error: ${errorText}`,
        response.status,
        response.statusText
      );
    }

    const data: ChatResponse = await response.json();
    return data.output;
  } catch (error) {
    if (error instanceof ChatApiError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ChatApiError(
        'Unable to connect to the backend. Please ensure the backend server is running.'
      );
    }

    throw new ChatApiError(
      error instanceof Error ? error.message : 'Unknown error occurred'
    );
  }
}
