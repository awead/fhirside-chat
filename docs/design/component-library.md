# Component Library - FHIRside Chat

Reference guide for all UI components with usage examples and props.

## Component Hierarchy

```
App
├── Header
│   ├── Logo
│   ├── SessionInfo
│   └── ActionsMenu
│       ├── NewSessionButton
│       └── SettingsButton
├── ChatContainer
│   ├── MessageList
│   │   └── Message (multiple)
│   │       ├── MessageBubble
│   │       ├── MessageTimestamp
│   │       └── TraceCountBadge
│   ├── TypingIndicator
│   └── MessageInput
│       ├── TextInput
│       └── SendButton
└── TelemetryPanel
    ├── TelemetryHeader
    │   ├── CollapseButton
    │   └── RefreshControls
    ├── FilterIndicator
    ├── SpanList
    │   └── SpanItem (multiple)
    │       ├── SpanHeader
    │       │   ├── SpanIcon
    │       │   ├── SpanName
    │       │   └── SpanDuration
    │       └── SpanDetail (expandable)
    │           ├── SpanMetadata
    │           ├── SpanAttributes
    │           └── CodeBlock
    └── EmptyState
```

---

## Core Components

### Header

Top navigation bar with session info and controls.

```tsx
interface HeaderProps {
  sessionId: string;
  onNewSession: () => void;
  onSettings: () => void;
}

<Header
  sessionId="abc-123"
  onNewSession={handleNewSession}
  onSettings={handleSettings}
/>
```

**Styling:**
- Height: 64px (mobile: 56px)
- Background: white
- Shadow: bottom shadow
- Padding: 16px horizontal

---

### ChatContainer

Main chat interface container.

```tsx
interface ChatContainerProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onMessageClick?: (messageId: string) => void;
}

<ChatContainer
  messages={messages}
  isLoading={isTyping}
  onSendMessage={sendMessage}
  onMessageClick={filterTelemetry}
/>
```

**Layout:**
- Max width: 800px
- Centered on screen
- Full height minus header/input
- Scroll container for messages

---

### Message

Individual chat message bubble.

```tsx
interface MessageProps {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  traceCount?: number;
  isActive?: boolean;
  onClick?: () => void;
}

<Message
  id="msg-1"
  role="user"
  content="How many patients?"
  timestamp={Date.now()}
  traceCount={3}
  onClick={() => filterByMessage('msg-1')}
/>
```

**Styling:**
- User: right-aligned, blue bg, white text
- Assistant: left-aligned, gray bg, dark text
- Max width: 70%
- Padding: 16px
- Border radius: 12px
- Margin: 12px vertical

---

### MessageInput

Text input and send button.

```tsx
interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isDisabled?: boolean;
  placeholder?: string;
}

<MessageInput
  value={inputValue}
  onChange={setInputValue}
  onSend={handleSend}
  isDisabled={isLoading}
  placeholder="Type a message..."
/>
```

**Behavior:**
- Enter key sends message
- Disabled during loading
- Auto-focus on mount
- Clear after send

---

### TypingIndicator

Animated indicator when assistant is typing.

```tsx
interface TypingIndicatorProps {
  isVisible: boolean;
}

<TypingIndicator isVisible={isLoading} />
```

**Animation:**
- Three dots pulsing
- Smooth fade in/out
- Left-aligned (assistant position)

---

## Telemetry Components

### TelemetryPanel

Main telemetry panel container.

```tsx
interface TelemetryPanelProps {
  sessionId: string;
  spans: SpanData[];
  isLoading: boolean;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  activeMessageId?: string;
  onClearFilter?: () => void;
}

<TelemetryPanel
  sessionId="abc-123"
  spans={telemetryData}
  isLoading={fetchingTraces}
  isCollapsed={panelCollapsed}
  onToggleCollapse={togglePanel}
  activeMessageId={filteredMessage}
  onClearFilter={clearFilter}
/>
```

**Layout (Desktop):**
- Width: 40% of viewport
- Min width: 320px
- Max width: 600px
- Fixed position right side
- Full height minus header

**Layout (Mobile):**
- Bottom drawer (slide up)
- Height: 60% of viewport
- Overlay with backdrop
- Swipe to dismiss

---

### SpanList

List of trace spans.

```tsx
interface SpanListProps {
  spans: SpanData[];
  onSpanClick?: (spanId: string) => void;
  expandedSpanIds?: string[];
}

<SpanList
  spans={filteredSpans}
  onSpanClick={handleSpanClick}
  expandedSpanIds={expandedIds}
/>
```

**Features:**
- Virtualized for performance (>100 spans)
- Scroll to top on filter change
- Empty state when no spans

---

### SpanItem

Individual span card (collapsed state).

```tsx
interface SpanItemProps {
  span: SpanData;
  isExpanded: boolean;
  onClick: () => void;
}

<SpanItem
  span={spanData}
  isExpanded={false}
  onClick={() => toggleSpan(spanData.span_id)}
/>
```

**Visual Differentiation:**
- OpenAI: Purple left border (4px), Brain icon
- MCP: Blue left border (4px), Database icon
- Error: Red left border, Alert icon

**Layout:**
- Height: 56px (collapsed)
- Padding: 12px
- Border radius: 8px
- Hover effect: background tint

---

### SpanDetail

Expanded span details view.

```tsx
interface SpanDetailProps {
  span: SpanData;
  onCopy?: (content: string) => void;
}

<SpanDetail
  span={expandedSpan}
  onCopy={copyToClipboard}
/>
```

**Content Sections:**
1. Metadata: Trace ID, Span ID, Parent ID
2. Timing: Start, End, Duration
3. OpenAI Data: Model, Prompt, Response, Tokens
4. MCP Data: Query, Resource Type, Response
5. Error Info: Error message, stack trace (if error)

**Features:**
- Syntax highlighting for JSON
- Copy buttons for code blocks
- Collapsible long content (>500 chars)

---

### RefreshControls

Manual and auto-refresh controls.

```tsx
interface RefreshControlsProps {
  isAutoRefresh: boolean;
  refreshInterval: number; // seconds
  lastUpdated: number; // timestamp
  onRefresh: () => void;
  onToggleAutoRefresh: () => void;
  onChangeInterval: (seconds: number) => void;
}

<RefreshControls
  isAutoRefresh={autoRefresh}
  refreshInterval={5}
  lastUpdated={lastFetchTime}
  onRefresh={fetchTelemetry}
  onToggleAutoRefresh={toggleAuto}
  onChangeInterval={setInterval}
/>
```

**Options:**
- Manual refresh button
- Auto-refresh toggle
- Interval selector: 5s, 10s, 30s, 60s
- Last updated timestamp

---

## Utility Components

### CodeBlock

Syntax-highlighted code display with copy button.

```tsx
interface CodeBlockProps {
  code: string;
  language: 'json' | 'javascript' | 'text';
  onCopy?: () => void;
  maxHeight?: number;
}

<CodeBlock
  code={JSON.stringify(data, null, 2)}
  language="json"
  onCopy={() => copyToClipboard(data)}
  maxHeight={400}
/>
```

**Features:**
- Syntax highlighting (react-syntax-highlighter)
- Copy button with feedback
- Scrollable if exceeds maxHeight
- Line numbers optional

---

### Badge

Small label badge (e.g., trace count).

```tsx
interface BadgeProps {
  count: number;
  variant?: 'default' | 'openai' | 'mcp';
  onClick?: () => void;
}

<Badge
  count={3}
  variant="default"
  onClick={handleBadgeClick}
/>
```

**Variants:**
- Default: Gray background
- OpenAI: Purple background
- MCP: Blue background

---

### EmptyState

Placeholder when no content.

```tsx
interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

<EmptyState
  icon={<MessageSquare />}
  title="No messages yet"
  description="Start a conversation by typing below"
  action={{
    label: "See examples",
    onClick: showExamples
  }}
/>
```

**Usage:**
- No messages in chat
- No traces in telemetry
- Error states (optional)

---

### LoadingSpinner

Animated loading indicator.

```tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

<LoadingSpinner
  size="md"
  label="Loading traces..."
/>
```

**Sizes:**
- sm: 16px
- md: 24px
- lg: 32px

---

## shadcn/ui Components Used

### Button

```tsx
import { Button } from '@/components/ui/button'

<Button
  variant="default" | "outline" | "ghost"
  size="default" | "sm" | "lg"
  onClick={handler}
>
  Send
</Button>
```

### Card

```tsx
import { Card } from '@/components/ui/card'

<Card className="p-4">
  {content}
</Card>
```

### Input

```tsx
import { Input } from '@/components/ui/input'

<Input
  type="text"
  placeholder="Type..."
  value={value}
  onChange={handler}
/>
```

### ScrollArea

```tsx
import { ScrollArea } from '@/components/ui/scroll-area'

<ScrollArea className="h-[600px]">
  {longContent}
</ScrollArea>
```

### Sheet (Mobile Drawer)

```tsx
import { Sheet, SheetContent, SheetHeader } from '@/components/ui/sheet'

<Sheet open={isOpen} onOpenChange={setIsOpen}>
  <SheetContent side="bottom">
    <SheetHeader>Telemetry</SheetHeader>
    {content}
  </SheetContent>
</Sheet>
```

---

## Icons (Lucide React)

### Used Icons

```tsx
import {
  Send,           // Send button
  Plus,           // New session
  Settings,       // Settings menu
  ChevronDown,    // Collapse
  ChevronUp,      // Expand
  Brain,          // OpenAI spans
  Database,       // MCP spans
  CheckCircle,    // Success status
  XCircle,        // Error status
  AlertCircle,    // Warning/error
  Loader2,        // Loading spinner
  Copy,           // Copy button
  RefreshCw,      // Manual refresh
  MessageSquare,  // Empty state
} from 'lucide-react'
```

### Icon Sizing

```tsx
// Small (metadata)
<Icon className="w-4 h-4" />

// Medium (default)
<Icon className="w-5 h-5" />

// Large (emphasis)
<Icon className="w-6 h-6" />
```

---

## Type Definitions

### Message

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  traceIds?: string[]; // Associated trace IDs
}
```

### SpanData

```typescript
interface SpanData {
  span_id: string;
  trace_id: string;
  parent_span_id?: string;
  operation_name: string;
  start_time: number;
  end_time: number;
  duration: number; // milliseconds
  attributes: SpanAttributes;
  status: 'OK' | 'ERROR';
  error_message?: string;
}

interface SpanAttributes {
  // OpenAI
  'openai.prompt'?: string;
  'openai.completion'?: string;
  'openai.model'?: string;
  'openai.token_count'?: number;

  // MCP
  'mcp.query'?: string;
  'mcp.resource_type'?: string;
  'mcp.response'?: string;

  // Common
  session_id: string;
}
```

### TelemetryResponse

```typescript
interface TelemetryResponse {
  session_id: string;
  spans: SpanData[];
  trace_count: number;
}
```

---

## Responsive Behavior

### Breakpoints

```typescript
const breakpoints = {
  mobile: '< 640px',
  tablet: '640px - 1024px',
  desktop: '> 1024px'
}
```

### Component Adaptations

| Component | Mobile | Desktop |
|-----------|--------|---------|
| ChatContainer | Full width | Max 800px centered |
| TelemetryPanel | Bottom drawer | Side panel (40%) |
| Message | Max 90% width | Max 70% width |
| Header | 56px height | 64px height |
| SpanItem | Full width | Full width |
| SpanDetail | Simplified | Full details |

---

## Animation Guidelines

### Timing Functions

```css
/* Fast interactions */
transition: 150ms ease-in-out

/* Standard interactions */
transition: 200ms ease-in-out

/* Slow/smooth transitions */
transition: 300ms ease-in-out
```

### Common Animations

```tsx
// Fade in
className="animate-in fade-in duration-200"

// Slide up (mobile drawer)
className="animate-in slide-in-from-bottom duration-300"

// Scale on hover
className="hover:scale-105 transition-transform duration-150"

// Spin (loading)
className="animate-spin"

// Pulse (typing indicator)
className="animate-pulse"
```

---

## Usage Examples

### Complete Chat Interface

```tsx
function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [spans, setSpans] = useState<SpanData[]>([]);
  const sessionId = getOrCreateSessionId();

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: inputValue,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendMessage(sessionId, inputValue);
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response,
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Fetch telemetry
      const telemetry = await fetchTelemetry(sessionId);
      setSpans(telemetry.spans);
    } catch (error) {
      // Handle error
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <ChatContainer
        messages={messages}
        isLoading={isLoading}
        onSendMessage={handleSend}
      />
      <TelemetryPanel
        sessionId={sessionId}
        spans={spans}
        isLoading={false}
      />
    </div>
  );
}
```

---

## Testing

### Component Testing

```tsx
// Example: Message component test
import { render, screen } from '@testing-library/react';
import { Message } from './Message';

test('renders user message with correct styling', () => {
  render(
    <Message
      id="1"
      role="user"
      content="Test message"
      timestamp={Date.now()}
    />
  );

  const message = screen.getByText('Test message');
  expect(message).toBeInTheDocument();
  expect(message).toHaveClass('bg-user-bg');
});
```

### Accessibility Testing

```tsx
import { axe, toHaveNoViolations } from 'jest-axe';

test('SpanItem has no accessibility violations', async () => {
  const { container } = render(<SpanItem span={mockSpan} />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## Implementation Priority

### Story 003 (React Chat Foundation)
1. ChatContainer
2. MessageList
3. Message
4. MessageInput
5. TypingIndicator

### Story 004 (Chat UI Enhancement)
1. Apply Tailwind styling to all Story 003 components
2. Add shadcn/ui components
3. Add icons
4. Responsive layout

### Story 005 (Telemetry Panel)
1. TelemetryPanel
2. SpanList
3. SpanItem
4. SpanDetail
5. RefreshControls
6. CodeBlock

---

This component library should be referenced during implementation of Stories 003-005.
