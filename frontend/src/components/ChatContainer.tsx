import { useState } from 'react';
import type { Message } from '../types/chat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { getOrCreateSessionId, createNewSession } from '../utils/session';
import { Button } from '@/components/ui/button';
import { RotateCcw, AlertCircle } from 'lucide-react';

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
      <div className="flex flex-col h-screen bg-background">
        <header className="px-6 py-4 bg-card border-b flex justify-between items-center">
          <div>
            <h1 className="text-xl font-semibold">FHIRside Chat</h1>
            <div className="text-xs text-muted-foreground mt-1">
              Session: {sessionId.substring(0, 8)}...
            </div>
          </div>
          <Button
            variant="outline"
            onClick={handleNewSession}
            disabled={isLoading}
            aria-label="Start new session"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            New Session
          </Button>
        </header>

        {error && (
          <div className="px-6 py-3 bg-destructive/10 text-destructive border-b text-sm flex items-center gap-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <MessageList messages={messages} />
        <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    ),
  };
}
