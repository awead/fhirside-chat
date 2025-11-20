import { useEffect, useRef } from 'react';
import type { Message as MessageType } from '../types/chat';
import { Message } from './Message';
import { ScrollArea } from '@/components/ui/scroll-area';

interface MessageListProps {
  messages: MessageType[];
}

export function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <ScrollArea className="flex-1">
      <div className="p-6 flex flex-col">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
            Start a conversation by typing a message below
          </div>
        ) : (
          messages.map((message) => <Message key={message.id} message={message} />)
        )}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
