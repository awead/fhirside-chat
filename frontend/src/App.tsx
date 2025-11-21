import { ChatContainer } from './components/ChatContainer';
import { TelemetryPanel } from './components/telemetry/TelemetryPanel';
import { ConnectionStatus } from './components/ConnectionStatus';
import { useWebSocket } from './hooks/useWebSocket';
import { getOrCreateSessionId } from './utils/session';

function App() {
  const sessionId = getOrCreateSessionId();
  const { isConnected, sendMessage, messages, telemetryEvents, error } =
    useWebSocket(sessionId);

  return (
    <div className="flex h-screen">
      <div className="flex-1 min-w-0">
        <ChatContainer
          sessionId={sessionId}
          messages={messages}
          sendMessage={sendMessage}
          isConnected={isConnected}
          error={error}
        />
      </div>
      <TelemetryPanel
        telemetryEvents={telemetryEvents}
        className="w-96 border-l h-full overflow-hidden"
      />
      <ConnectionStatus isConnected={isConnected} sessionId={sessionId} />
    </div>
  );
}

export default App;
