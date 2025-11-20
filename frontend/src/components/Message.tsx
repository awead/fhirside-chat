import type { Message as MessageType } from '../types/chat';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface MessageProps {
  message: MessageType;
}

function formatTimestamp(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 10) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex flex-col mb-3', isUser ? 'items-end' : 'items-start')}>
      <Card
        className={cn(
          'max-w-[80%] p-4',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted text-foreground'
        )}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
      </Card>
      <div className="text-xs text-muted-foreground mt-1 px-2">
        {formatTimestamp(message.timestamp)}
      </div>
    </div>
  );
}
