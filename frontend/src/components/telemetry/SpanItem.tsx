import { useState, lazy, Suspense } from 'react';
import { Card } from '@/components/ui/card';
import { Brain, Database, CheckCircle, XCircle, ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SpanData } from '@/types/telemetry';
import { getSpanType, formatDuration, formatTimestamp } from '@/types/telemetry';

const SpanDetail = lazy(() =>
  import('./SpanDetail').then((module) => ({ default: module.SpanDetail }))
);

interface SpanItemProps {
  span: SpanData;
}

const spanStyles = {
  openai: {
    borderColor: 'border-l-purple-500',
    borderWidth: 'border-l-4',
    hoverBg: 'hover:bg-purple-50',
    icon: Brain,
    iconColor: 'text-purple-500',
    badgeBg: 'bg-purple-100',
    badgeText: 'text-purple-700',
  },
  mcp: {
    borderColor: 'border-l-blue-500',
    borderWidth: 'border-l-4',
    hoverBg: 'hover:bg-blue-50',
    icon: Database,
    iconColor: 'text-blue-500',
    badgeBg: 'bg-blue-100',
    badgeText: 'text-blue-700',
  },
  unknown: {
    borderColor: 'border-l-gray-400',
    borderWidth: 'border-l-4',
    hoverBg: 'hover:bg-gray-50',
    icon: Database,
    iconColor: 'text-gray-500',
    badgeBg: 'bg-gray-100',
    badgeText: 'text-gray-700',
  },
};

export function SpanItem({ span }: SpanItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const type = getSpanType(span.operation_name);
  const styles = spanStyles[type];
  const Icon = styles.icon;

  return (
    <Card
      className={cn(
        'cursor-pointer transition-colors mb-2',
        styles.borderColor,
        styles.borderWidth,
        styles.hoverBg
      )}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="p-3">
        <div className="flex items-center gap-3">
          <Icon className={cn('w-5 h-5 flex-shrink-0', styles.iconColor)} />

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-sm truncate">{span.operation_name}</span>
              <span className={cn('px-2 py-0.5 rounded text-xs font-medium', styles.badgeBg, styles.badgeText)}>
                {type.toUpperCase()}
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span>{formatTimestamp(span.start_time)}</span>
              <span>·</span>
              <span>{formatDuration(span.duration)}</span>
              <span>·</span>
              <span className="truncate">Trace: {span.trace_id.substring(0, 8)}...</span>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            {span.status === 'OK' ? (
              <CheckCircle className="w-4 h-4 text-green-600" />
            ) : (
              <XCircle className="w-4 h-4 text-red-600" />
            )}
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            )}
          </div>
        </div>

        {isExpanded && (
          <Suspense fallback={<div className="mt-3 pt-3 border-t text-sm text-muted-foreground">Loading details...</div>}>
            <SpanDetail span={span} />
          </Suspense>
        )}
      </div>
    </Card>
  );
}
