import { useState } from 'react';
import { ChatContainer } from './components/ChatContainer';
import { TelemetryPanel } from './components/telemetry/TelemetryPanel';
import { sendMessage, ChatApiError } from './services/chatApi';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const chatContainer = ChatContainer({
    onSendMessage: async (sessionId: string, message: string) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await sendMessage(sessionId, message);
        chatContainer.addAssistantMessage(response);
      } catch (err) {
        const errorMessage =
          err instanceof ChatApiError
            ? err.message
            : 'An unexpected error occurred';
        setError(errorMessage);
        console.error('Chat error:', err);
      } finally {
        setIsLoading(false);
      }
    },
    isLoading,
    error,
  });

  return (
    <div className="flex h-screen">
      <div className="flex-1 min-w-0">{chatContainer.renderUI()}</div>
      <TelemetryPanel
        sessionId={chatContainer.sessionId}
        className="w-96 border-l h-full overflow-hidden"
      />
    </div>
  );
}

export default App;
