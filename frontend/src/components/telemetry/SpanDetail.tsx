import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Button } from '@/components/ui/button';
import { Copy, Check } from 'lucide-react';
import type { SpanData, SpanAttributes } from '@/types/telemetry';
import { formatDuration, formatTimestamp, getSpanType } from '@/types/telemetry';

interface SpanDetailProps {
  span: SpanData;
}

interface CopyButtonProps {
  text: string;
  label?: string;
}

function CopyButton({ text, label = 'Copy' }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleCopy}
      className="h-7 text-xs"
      aria-label={label}
    >
      {copied ? (
        <>
          <Check className="h-3 w-3 mr-1" />
          Copied
        </>
      ) : (
        <>
          <Copy className="h-3 w-3 mr-1" />
          Copy
        </>
      )}
    </Button>
  );
}

interface AttributeDisplayProps {
  label: string;
  value: string | number | undefined;
  copyable?: boolean;
  language?: string;
}

function AttributeDisplay({ label, value, copyable = false, language }: AttributeDisplayProps) {
  const stringValue = typeof value === 'string' ? value : String(value);
  const isLongContent = stringValue.length > 500;
  const [expanded, setExpanded] = useState(!isLongContent);

  if (value === undefined) return null;

  const renderValue = () => {
    if (language && language === 'json') {
      try {
        const parsed = JSON.parse(stringValue);
        const formatted = JSON.stringify(parsed, null, 2);
        return (
          <div className="relative group">
            <SyntaxHighlighter
              language="json"
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                borderRadius: '0.375rem',
                fontSize: '0.75rem',
                maxHeight: expanded ? 'none' : '200px',
                overflow: 'auto',
              }}
            >
              {formatted}
            </SyntaxHighlighter>
            {copyable && (
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <CopyButton text={formatted} />
              </div>
            )}
          </div>
        );
      } catch {
        // Fall through to plain text if JSON parse fails
      }
    }

    return (
      <div className="relative bg-muted p-3 rounded-md text-xs font-mono group">
        <pre className="whitespace-pre-wrap break-words" style={{ maxHeight: expanded ? 'none' : '200px', overflow: 'auto' }}>
          {expanded ? stringValue : stringValue.substring(0, 500) + '...'}
        </pre>
        {copyable && (
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <CopyButton text={stringValue} />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <label className="text-xs font-medium text-muted-foreground">{label}</label>
        {isLongContent && (
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
            className="h-6 text-xs"
          >
            {expanded ? 'Show less' : 'Show more'}
          </Button>
        )}
      </div>
      {renderValue()}
    </div>
  );
}

function renderOpenAIAttributes(attributes: SpanAttributes) {
  return (
    <>
      <AttributeDisplay label="Model" value={attributes['openai.model']} />
      <AttributeDisplay label="Token Count" value={attributes['openai.token_count']} />
      <AttributeDisplay label="Prompt" value={attributes['openai.prompt']} copyable language="json" />
      <AttributeDisplay label="Completion" value={attributes['openai.completion']} copyable language="json" />
    </>
  );
}

function renderMCPAttributes(attributes: SpanAttributes) {
  return (
    <>
      <AttributeDisplay label="Resource Type" value={attributes['mcp.resource_type']} />
      <AttributeDisplay label="Query" value={attributes['mcp.query']} copyable language="json" />
      <AttributeDisplay label="Response" value={attributes['mcp.response']} copyable language="json" />
    </>
  );
}

export function SpanDetail({ span }: SpanDetailProps) {
  const spanType = getSpanType(span.operation_name);

  return (
    <div className="mt-3 pt-3 border-t space-y-3">
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <label className="text-muted-foreground">Span ID</label>
          <p className="font-mono mt-1">{span.span_id}</p>
        </div>
        <div>
          <label className="text-muted-foreground">Trace ID</label>
          <p className="font-mono mt-1">{span.trace_id}</p>
        </div>
        {span.parent_span_id && (
          <div className="col-span-2">
            <label className="text-muted-foreground">Parent Span ID</label>
            <p className="font-mono mt-1">{span.parent_span_id}</p>
          </div>
        )}
        <div>
          <label className="text-muted-foreground">Start Time</label>
          <p className="mt-1">{formatTimestamp(span.start_time)}</p>
        </div>
        <div>
          <label className="text-muted-foreground">Duration</label>
          <p className="mt-1">{formatDuration(span.duration)}</p>
        </div>
        <div>
          <label className="text-muted-foreground">Status</label>
          <p className="mt-1">{span.status}</p>
        </div>
      </div>

      {span.error_message && (
        <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
          <strong>Error:</strong> {span.error_message}
        </div>
      )}

      <div className="pt-2">
        <h4 className="text-sm font-semibold mb-3">Attributes</h4>
        {spanType === 'openai' && renderOpenAIAttributes(span.attributes)}
        {spanType === 'mcp' && renderMCPAttributes(span.attributes)}
        {spanType === 'unknown' && (
          <AttributeDisplay
            label="All Attributes"
            value={JSON.stringify(span.attributes, null, 2)}
            copyable
            language="json"
          />
        )}
      </div>
    </div>
  );
}
