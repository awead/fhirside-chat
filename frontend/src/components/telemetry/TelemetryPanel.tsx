import { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Activity, RefreshCw, Play, Pause } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SpanData } from '@/types/telemetry';
import { fetchTelemetry, TelemetryApiError } from '@/services/telemetryApi';
import { SpanList } from './SpanList';

interface TelemetryPanelProps {
  sessionId: string;
  className?: string;
}

const STORAGE_KEY_COLLAPSED = 'telemetry-panel-collapsed';
const STORAGE_KEY_AUTO_REFRESH = 'telemetry-auto-refresh';
const STORAGE_KEY_INTERVAL = 'telemetry-refresh-interval';

export function TelemetryPanel({ sessionId, className }: TelemetryPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY_COLLAPSED);
    return stored === 'true';
  });
  const [spans, setSpans] = useState<SpanData[]>([]);
  const [traceCount, setTraceCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY_AUTO_REFRESH);
    return stored === 'true';
  });
  const [refreshInterval] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY_INTERVAL);
    return stored ? parseInt(stored, 10) : 5000;
  });

  const loadTelemetry = useCallback(async () => {
    if (!sessionId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchTelemetry(sessionId);
      setSpans(data.spans);
      setTraceCount(data.trace_count);
      setLastUpdated(new Date());
    } catch (err) {
      if (err instanceof TelemetryApiError) {
        if (err.status === 404) {
          setError('No telemetry data found for this session');
        } else {
          setError(`Failed to load telemetry: ${err.message}`);
        }
      } else {
        setError('An unexpected error occurred');
      }
      setSpans([]);
      setTraceCount(0);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadTelemetry();
  }, [loadTelemetry]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_COLLAPSED, String(isCollapsed));
  }, [isCollapsed]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_AUTO_REFRESH, String(autoRefresh));
  }, [autoRefresh]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY_INTERVAL, String(refreshInterval));
  }, [refreshInterval]);

  useEffect(() => {
    if (!autoRefresh || isCollapsed) return;

    const intervalId = setInterval(() => {
      loadTelemetry();
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [autoRefresh, isCollapsed, refreshInterval, loadTelemetry]);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <Card className={cn('flex flex-col', className)}>
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          <Activity className="h-5 w-5 text-muted-foreground" />
          <div>
            <h2 className="text-lg font-semibold">Telemetry</h2>
            <p className="text-xs text-muted-foreground">
              {traceCount} {traceCount === 1 ? 'trace' : 'traces'} · {spans.length}{' '}
              {spans.length === 1 ? 'span' : 'spans'}
              {lastUpdated && (
                <> · Updated {lastUpdated.toLocaleTimeString()}</>
              )}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={autoRefresh ? "default" : "ghost"}
            size="icon"
            onClick={() => setAutoRefresh(!autoRefresh)}
            aria-label={autoRefresh ? 'Disable auto-refresh' : 'Enable auto-refresh'}
            title={autoRefresh ? `Auto-refreshing every ${refreshInterval / 1000}s` : 'Enable auto-refresh'}
          >
            {autoRefresh ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={loadTelemetry}
            disabled={isLoading}
            aria-label="Refresh telemetry"
          >
            <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
          </Button>
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
      </div>

      {!isCollapsed && (
        <div className="flex-1 overflow-auto">
          {error && (
            <div className="p-4 text-sm text-destructive bg-destructive/10 border-b">
              {error}
            </div>
          )}

          {!isLoading && !error && spans.length === 0 && (
            <div className="flex flex-col items-center justify-center p-12 text-center">
              <Activity className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <p className="text-sm text-muted-foreground">
                No traces available for this session
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Send a message to generate telemetry data
              </p>
            </div>
          )}

          {spans.length > 0 && (
            <div className="p-4">
              <SpanList spans={spans} />
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
