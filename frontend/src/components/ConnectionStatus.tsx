import { Wifi, WifiOff } from "lucide-react";

interface ConnectionStatusProps {
  isConnected: boolean;
  sessionId: string;
  isReconnecting?: boolean;
}

export function ConnectionStatus({
  isConnected,
  sessionId,
  isReconnecting = false,
}: ConnectionStatusProps) {
  const status = isReconnecting
    ? "reconnecting"
    : isConnected
      ? "connected"
      : "disconnected";

  const statusColor =
    status === "connected"
      ? "text-green-600"
      : status === "reconnecting"
        ? "text-yellow-600"
        : "text-red-600";

  const Icon = status === "disconnected" ? WifiOff : Wifi;

  const statusText =
    status === "connected"
      ? `Connected (session: ${sessionId})`
      : status === "reconnecting"
        ? "Reconnecting..."
        : "Disconnected";

  return (
    <div
      className="fixed top-4 right-4 flex items-center gap-2 rounded-lg bg-white px-3 py-2 shadow-md"
      role="status"
      aria-live="polite"
      aria-label={statusText}
    >
      <Icon
        className={`h-4 w-4 ${statusColor} ${status === "reconnecting" ? "animate-pulse" : ""}`}
        aria-hidden="true"
      />
      <span className={`text-sm font-medium ${statusColor}`}>{status}</span>
      {sessionId && (
        <span className="text-xs text-gray-500" title={statusText}>
          {sessionId.slice(0, 8)}
        </span>
      )}
    </div>
  );
}
