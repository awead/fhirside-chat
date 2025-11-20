import { useState } from 'react';
import type { Message } from '../types/chat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { getOrCreateSessionId, createNewSession } from '../utils/session';

interface ChatContainerProps {
  onSendMessage: (sessionId: string, message: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export function ChatContainer({
  onSendMessage,
  isLoading,
  error,
}: ChatContainerProps) {
  const [sessionId, setSessionId] = useState(() => getOrCreateSessionId());
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSendMessage = async (messageContent: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: messageContent,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      await onSendMessage(sessionId, messageContent);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const handleNewSession = () => {
    const newSessionId = createNewSession();
    setSessionId(newSessionId);
    setMessages([]);
  };

  const addAssistantMessage = (content: string) => {
    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
  };

  return {
    sessionId,
    messages,
    handleSendMessage,
    handleNewSession,
    addAssistantMessage,
    renderUI: () => (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          backgroundColor: '#f8f9fa',
        }}
      >
        <div
          style={{
            padding: '16px 20px',
            backgroundColor: 'white',
            borderBottom: '1px solid #dee2e6',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
              FHIRside Chat
            </h1>
            <div style={{ fontSize: '12px', color: '#6c757d', marginTop: '4px' }}>
              Session: {sessionId.substring(0, 8)}...
            </div>
          </div>
          <button
            onClick={handleNewSession}
            disabled={isLoading}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: '1px solid #ced4da',
              backgroundColor: 'white',
              color: '#495057',
              fontSize: '14px',
              fontWeight: '500',
              cursor: isLoading ? 'not-allowed' : 'pointer',
            }}
          >
            New Session
          </button>
        </div>

        {error && (
          <div
            style={{
              padding: '12px 20px',
              backgroundColor: '#f8d7da',
              color: '#721c24',
              borderBottom: '1px solid #f5c6cb',
              fontSize: '14px',
            }}
          >
            ⚠️ {error}
          </div>
        )}

        <MessageList messages={messages} />
        <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    ),
  };
}
