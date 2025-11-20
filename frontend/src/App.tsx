import { useState } from 'react';
import { ChatContainer } from './components/ChatContainer';
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

  return chatContainer.renderUI();
}

export default App;
