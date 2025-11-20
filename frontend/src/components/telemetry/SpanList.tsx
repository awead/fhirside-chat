import { useMemo } from 'react';
import type { SpanData } from '@/types/telemetry';
import { SpanItem } from './SpanItem';

interface SpanListProps {
  spans: SpanData[];
  sortOrder?: 'asc' | 'desc';
}

export function SpanList({ spans, sortOrder = 'desc' }: SpanListProps) {
  const sortedSpans = useMemo(() => {
    const sorted = [...spans].sort((a, b) => {
      if (sortOrder === 'asc') {
        return a.start_time - b.start_time;
      }
      return b.start_time - a.start_time;
    });
    return sorted;
  }, [spans, sortOrder]);

  if (spans.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      {sortedSpans.map((span) => (
        <SpanItem key={span.span_id} span={span} />
      ))}
    </div>
  );
}
