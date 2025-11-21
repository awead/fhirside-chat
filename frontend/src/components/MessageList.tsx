import { useEffect, useRef } from 'react';
import type { AssistantMessage } from '../types/websocket';
import { StreamingMessage } from './StreamingMessage';
import { ScrollArea } from '@/components/ui/scroll-area';

interface MessageListProps {
  messages: AssistantMessage[];
}

export function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <ScrollArea className="flex-1">
      <div className="p-6 flex flex-col gap-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
            Start a conversation by typing a message below
          </div>
        ) : (
          messages.map((message, idx) => (
            <div key={idx} className="bg-card rounded-lg p-4 border">
              <div className="text-sm font-medium text-muted-foreground mb-2">
                Assistant
              </div>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                {message.streaming ? (
                  <StreamingMessage content={message.content} />
                ) : (
                  message.content
                )}
              </div>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
