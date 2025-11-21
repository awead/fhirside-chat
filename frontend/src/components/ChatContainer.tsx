import type { AssistantMessage } from '../types/websocket';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { createNewSession } from '../utils/session';
import { Button } from '@/components/ui/button';
import { RotateCcw, AlertCircle } from 'lucide-react';

interface ChatContainerProps {
  sessionId: string;
  messages: AssistantMessage[];
  sendMessage: (content: string) => void;
  isConnected: boolean;
  error: string | null;
}

export function ChatContainer({
  sessionId,
  messages,
  sendMessage,
  isConnected,
  error,
}: ChatContainerProps) {
  const handleSendMessage = (messageContent: string) => {
    sendMessage(messageContent);
  };

  const handleNewSession = () => {
    createNewSession();
    window.location.reload();
  };

  return (
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
          disabled={!isConnected}
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
      <MessageInput onSendMessage={handleSendMessage} disabled={!isConnected} />
    </div>
  );
}
