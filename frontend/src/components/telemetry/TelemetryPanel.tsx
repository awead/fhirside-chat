import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { TelemetryEvent } from '@/types/websocket';

interface TelemetryPanelProps {
  telemetryEvents: TelemetryEvent[];
  className?: string;
}

const STORAGE_KEY_COLLAPSED = 'telemetry-panel-collapsed';

export function TelemetryPanel({ telemetryEvents, className }: TelemetryPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY_COLLAPSED);
    return stored === 'true';
  });
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_COLLAPSED, String(isCollapsed));
  }, [isCollapsed]);

  useEffect(() => {
    if (panelRef.current && !isCollapsed) {
      panelRef.current.scrollTop = panelRef.current.scrollHeight;
    }
  }, [telemetryEvents, isCollapsed]);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const getEventColor = (event: TelemetryEvent): string => {
    if (event.type === 'openai_call' || event.type === 'openai_response') {
      return 'text-purple-600 bg-purple-50';
    }
    return 'text-blue-600 bg-blue-50';
  };

  const getEventLabel = (event: TelemetryEvent): string => {
    switch (event.type) {
      case 'tool_call':
        return `Tool Call: ${event.tool_name}`;
      case 'tool_result':
        return `Tool Result: ${event.tool_name} (${event.duration_ms}ms)`;
      case 'openai_call':
        return `OpenAI Call: ${event.model}`;
      case 'openai_response':
        return `OpenAI Response: ${event.model} (${event.duration_ms}ms)`;
      default:
        return 'Unknown Event';
    }
  };

  return (
    <Card className={cn('flex flex-col', className)}>
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          <Activity className="h-5 w-5 text-muted-foreground" />
          <div>
            <h2 className="text-lg font-semibold">Real-Time Telemetry</h2>
            <p className="text-xs text-muted-foreground">
              {telemetryEvents.length} {telemetryEvents.length === 1 ? 'event' : 'events'}
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleCollapse}
          aria-label={isCollapsed ? 'Expand telemetry panel' : 'Collapse telemetry panel'}
        >
          {isCollapsed ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </Button>
      </div>

      {!isCollapsed && (
        <div ref={panelRef} className="flex-1 overflow-auto p-4">
          {telemetryEvents.length === 0 && (
            <div className="flex flex-col items-center justify-center p-12 text-center">
              <Activity className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <p className="text-sm text-muted-foreground">
                No telemetry events yet
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Send a message to see real-time telemetry
              </p>
            </div>
          )}

          {telemetryEvents.length > 0 && (
            <div className="space-y-2">
              {telemetryEvents.map((event, idx) => (
                <div
                  key={idx}
                  className={cn(
                    'p-3 rounded-lg border text-sm',
                    getEventColor(event)
                  )}
                >
                  <div className="font-medium">{getEventLabel(event)}</div>
                  <div className="text-xs mt-1 opacity-75">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
