# Story 009: Streaming UI Updates

**Status:** Draft
**Epic:** 003 - Real-Time WebSocket Chat & Telemetry
**Story Points:** 3
**Estimated Hours:** 5-6 hours
**Dependencies:** Stories 006 (Backend), 007 (Telemetry), 008 (Frontend Client)

## Story

**As a** user,
**I want** chat messages to display progressively as they're received and telemetry to update in real-time,
**so that** I have immediate feedback on system operations.

## Acceptance Criteria

1. **ChatContainer Handles Streaming Messages**
   - ChatContainer component updated to use useWebSocket hook
   - Displays AssistantMessage content progressively (if streaming: true)
   - UserMessage displayed immediately on send
   - Chat history preserved and scrolls to bottom on new messages
   - Remove REST API calls (deprecated)

2. **StreamingMessage Component Created**
   - New component in `frontend/src/components/StreamingMessage.tsx`
   - Renders text character-by-character (typewriter effect)
   - Configurable speed (default 20ms per character)
   - Skippable (click to show full message instantly)
   - Maintains accessibility (screen reader reads full text)

3. **TelemetryPanel Shows Real-Time Events**
   - TelemetryPanel updated to consume telemetryEvents from useWebSocket
   - Remove REST polling logic (no more 5-second intervals)
   - Remove refresh button (no longer needed)
   - Display ToolCallEvent, ToolResultEvent, OpenAIEvent as they arrive
   - Maintain existing visual design (OpenAI purple, MCP blue)
   - Auto-scroll to latest event

4. **App.tsx Integrates useWebSocket Hook**
   - App component uses useWebSocket instead of REST chatApi
   - Pass session_id from localStorage
   - Pass WebSocket state to ChatContainer and TelemetryPanel
   - Add ConnectionStatus component to header
   - Remove deprecated REST API imports

5. **Accessibility Compliance Maintained**
   - Streaming messages accessible to screen readers (full text available)
   - Telemetry panel keyboard navigable
   - Connection status has aria-label
   - Live region for new messages (aria-live="polite")
   - Verify with axe DevTools (0 critical violations)
   - Lighthouse Accessibility score ≥ 90

6. **Component Tests Updated**
   - ChatContainer tests updated for WebSocket
   - TelemetryPanel tests updated for real-time events
   - StreamingMessage component tested
   - Mock useWebSocket hook in tests
   - Existing tests pass (no regressions)

7. **Integration Checkpoint**
   - End-to-end chat flow working with real-time telemetry
   - Send message, see streaming response + telemetry events
   - No console errors or warnings
   - Smooth user experience (no lag, no flash of content)
   - Multiple sessions work independently (different browser tabs)

## Tasks / Subtasks

- [ ] **Task 1: Create StreamingMessage Component** (AC: 2)
  - [ ] Create `frontend/src/components/StreamingMessage.tsx`
  - [ ] Accept props: `content: string`, `speed?: number` (default 20)
  - [ ] Use `useState` for displayedText and `useEffect` for animation
  - [ ] Implement character-by-character reveal:
    ```typescript
    useEffect(() => {
      if (displayedText.length < content.length) {
        const timeout = setTimeout(() => {
          setDisplayedText(content.slice(0, displayedText.length + 1));
        }, speed);
        return () => clearTimeout(timeout);
      }
    }, [displayedText, content, speed]);
    ```
  - [ ] Add click handler to skip animation (show full text)
  - [ ] Add aria-label with full content for screen readers
  - [ ] Style with existing TailwindCSS classes
  - [ ] Write component tests: `StreamingMessage.test.tsx`

- [ ] **Task 2: Update ChatContainer for WebSocket** (AC: 1)
  - [ ] Open `frontend/src/components/ChatContainer.tsx`
  - [ ] Remove REST chatApi import
  - [ ] Accept props from useWebSocket: `{ messages, sendMessage, isConnected }`
  - [ ] Update sendMessage handler to use WebSocket sendMessage
  - [ ] Render UserMessage immediately on send (optimistic UI)
  - [ ] Render AssistantMessage using StreamingMessage component
  - [ ] Check message.streaming flag: if true, use StreamingMessage; else show full text
  - [ ] Auto-scroll to bottom on new messages (existing behavior)
  - [ ] Disable input when not connected (isConnected === false)
  - [ ] Update component tests to mock useWebSocket

- [ ] **Task 3: Update TelemetryPanel for Real-Time Events** (AC: 3)
  - [ ] Open `frontend/src/components/telemetry/TelemetryPanel.tsx`
  - [ ] Remove REST telemetryApi import
  - [ ] Remove polling logic (useEffect with setInterval)
  - [ ] Remove refresh button from UI
  - [ ] Accept telemetryEvents prop from useWebSocket
  - [ ] Render events as they arrive (no manual refresh needed)
  - [ ] Maintain existing visual design:
    - ToolCallEvent / ToolResultEvent: Blue (MCP)
    - OpenAIEvent: Purple (OpenAI)
  - [ ] Auto-scroll to latest event on new arrival
  - [ ] Update component tests to use static telemetryEvents prop

- [ ] **Task 4: Integrate useWebSocket in App.tsx** (AC: 4)
  - [ ] Open `frontend/src/App.tsx`
  - [ ] Remove REST API imports: `chatApi.ts`, `telemetryApi.ts`
  - [ ] Get session_id from localStorage (existing pattern)
  - [ ] Add useWebSocket hook:
    ```typescript
    const { isConnected, sendMessage, messages, telemetryEvents, error } =
      useWebSocket(sessionId);
    ```
  - [ ] Pass props to ChatContainer: `{ messages, sendMessage, isConnected }`
  - [ ] Pass props to TelemetryPanel: `{ telemetryEvents }`
  - [ ] Add ConnectionStatus component to header:
    ```typescript
    <header>
      <h1>FHIRside Chat</h1>
      <ConnectionStatus isConnected={isConnected} sessionId={sessionId} />
    </header>
    ```
  - [ ] Display error if present: `{error && <div className="error">{error}</div>}`

- [ ] **Task 5: Verify Accessibility Compliance** (AC: 5)
  - [ ] Install axe DevTools browser extension if not installed
  - [ ] Run Lighthouse audit in Chrome DevTools
  - [ ] Verify StreamingMessage has aria-label with full content
  - [ ] Add aria-live="polite" to message container for new messages
  - [ ] Verify ConnectionStatus has aria-label
  - [ ] Test keyboard navigation:
    - [ ] Tab to input field
    - [ ] Tab to send button
    - [ ] Tab through telemetry items
  - [ ] Test with screen reader (VoiceOver on Mac or NVDA on Windows)
  - [ ] Run axe DevTools scan, verify 0 critical violations
  - [ ] Run Lighthouse, verify Accessibility score ≥ 90
  - [ ] Document any issues found and fixed

- [ ] **Task 6: Update Component Tests** (AC: 6)
  - [ ] Update `ChatContainer.test.tsx`:
    - [ ] Mock useWebSocket hook
    - [ ] Test sending message calls sendMessage prop
    - [ ] Test messages render correctly
    - [ ] Test streaming vs non-streaming messages
    - [ ] Test disabled input when disconnected
  - [ ] Update `TelemetryPanel.test.tsx`:
    - [ ] Remove polling tests (no longer applicable)
    - [ ] Test telemetryEvents render correctly
    - [ ] Test event type visual distinction (colors)
  - [ ] Create `StreamingMessage.test.tsx`:
    - [ ] Test character-by-character rendering
    - [ ] Test skip on click
    - [ ] Test aria-label present
  - [ ] Update `App.test.tsx`:
    - [ ] Mock useWebSocket hook
    - [ ] Test ConnectionStatus rendered
    - [ ] Test error displayed if present
  - [ ] Run all tests: `npm test`
  - [ ] Verify no test failures

- [ ] **Task 7: Integration Testing & Checkpoint** (AC: 7)
  - [ ] Start backend: `uv run uvicorn src:app --port 8000 --reload`
  - [ ] Start frontend: `npm run dev`
  - [ ] Open browser to `http://localhost:5173`
  - [ ] Verify ConnectionStatus shows green (connected)
  - [ ] Send test message: "What is quintin cole's diagnosis?"
  - [ ] Observe streaming response (character-by-character)
  - [ ] Observe telemetry events appear in real-time:
    - [ ] ToolCallEvent (blue, MCP)
    - [ ] ToolResultEvent (blue, MCP)
    - [ ] OpenAIEvent (purple, OpenAI)
  - [ ] Verify auto-scroll to latest events
  - [ ] Open second browser tab with different URL param (different session)
  - [ ] Verify both sessions work independently (no cross-contamination)
  - [ ] Check browser console (no errors or warnings)
  - [ ] Click streaming message to skip animation (instant full text)
  - [ ] Stop backend, verify ConnectionStatus shows yellow (reconnecting)
  - [ ] Restart backend, verify reconnection (green again)

## Dev Notes

### Previous Story Insights
- **Story 006** implemented backend WebSocket infrastructure
- **Story 007** added real-time telemetry emission
- **Story 008** created useWebSocket hook and ConnectionStatus component
- All backend and frontend infrastructure is ready for UI integration

### StreamingMessage Component Specification
[Source: Epic 003, Section "Component Architecture"]

**Purpose:** Progressive text rendering for ChatGPT-style streaming effect

**Component Interface:**
```typescript
interface StreamingMessageProps {
  content: string;
  speed?: number; // milliseconds per character, default 20
  onComplete?: () => void;
}
```

**Implementation Pattern:**
```typescript
export function StreamingMessage({ content, speed = 20, onComplete }: StreamingMessageProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (displayedText.length < content.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(content.slice(0, displayedText.length + 1));
      }, speed);
      return () => clearTimeout(timeout);
    } else if (!isComplete) {
      setIsComplete(true);
      onComplete?.();
    }
  }, [displayedText, content, speed, isComplete, onComplete]);

  const skipAnimation = () => {
    setDisplayedText(content);
    setIsComplete(true);
  };

  return (
    <div
      onClick={skipAnimation}
      aria-label={content}
      className="cursor-pointer"
    >
      {displayedText}
      {!isComplete && <span className="animate-pulse">▋</span>}
    </div>
  );
}
```

**Accessibility:**
- Full content in aria-label (screen readers read full text immediately)
- Click to skip animation (user control)
- Visual cursor indicator (▋ or |) while streaming

### ChatContainer Integration
[Source: Frontend components from Epic 002, adapted for WebSocket]

**Current state:** Uses REST chatApi with fetch
**New state:** Uses useWebSocket hook

**Changes needed:**
```typescript
// Before (REST)
import { sendMessage as apiSendMessage } from '../services/chatApi';

// After (WebSocket)
interface ChatContainerProps {
  messages: AssistantMessage[];
  sendMessage: (content: string) => void;
  isConnected: boolean;
}

function ChatContainer({ messages, sendMessage, isConnected }: ChatContainerProps) {
  const handleSend = (content: string) => {
    // Optimistic UI: show user message immediately
    // WebSocket will echo back for consistency
    sendMessage(content);
  };

  return (
    <div>
      {messages.map((msg, idx) => (
        msg.streaming ?
          <StreamingMessage key={idx} content={msg.content} /> :
          <div key={idx}>{msg.content}</div>
      ))}
      <input
        disabled={!isConnected}
        onSubmit={handleSend}
      />
    </div>
  );
}
```

### TelemetryPanel Integration
[Source: Frontend components from Epic 002, adapted for real-time]

**Current state:** Polls REST `/telemetry/{session_id}` every 5 seconds
**New state:** Receives real-time events from useWebSocket

**Changes needed:**
```typescript
// Remove polling
// Before:
useEffect(() => {
  const interval = setInterval(() => {
    fetchTelemetry(sessionId);
  }, 5000);
  return () => clearInterval(interval);
}, [sessionId]);

// After: No polling, just render telemetryEvents
interface TelemetryPanelProps {
  telemetryEvents: (ToolCallEvent | ToolResultEvent | OpenAIEvent)[];
}

function TelemetryPanel({ telemetryEvents }: TelemetryPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to latest event
    panelRef.current?.scrollTo({ top: panelRef.current.scrollHeight, behavior: 'smooth' });
  }, [telemetryEvents]);

  return (
    <div ref={panelRef} className="overflow-y-auto">
      {telemetryEvents.map((event, idx) => (
        <TelemetryEvent key={idx} event={event} />
      ))}
    </div>
  );
}
```

**Visual Design:** Maintain existing colors from Story 005:
- OpenAI events: Purple (#9333EA or similar)
- MCP/Tool events: Blue (#3B82F6 or similar)

### App.tsx Integration Pattern
[Source: Frontend architecture]

**Current architecture:** REST API calls from App.tsx
**New architecture:** useWebSocket hook provides all state

```typescript
// App.tsx
import { useWebSocket } from './hooks/useWebSocket';
import { ConnectionStatus } from './components/ConnectionStatus';
import { ChatContainer } from './components/ChatContainer';
import { TelemetryPanel } from './components/telemetry/TelemetryPanel';

function App() {
  const sessionId = localStorage.getItem('session_id') || generateSessionId();
  const { isConnected, sendMessage, messages, telemetryEvents, error } =
    useWebSocket(sessionId);

  return (
    <div className="app">
      <header>
        <h1>FHIRside Chat</h1>
        <ConnectionStatus isConnected={isConnected} sessionId={sessionId} />
      </header>
      {error && <div className="error-banner">{error}</div>}
      <main>
        <ChatContainer
          messages={messages}
          sendMessage={sendMessage}
          isConnected={isConnected}
        />
        <TelemetryPanel telemetryEvents={telemetryEvents} />
      </main>
    </div>
  );
}
```

### File Locations
[Source: Epic 003, Section "File Organization"]

**New Files:**
- `frontend/src/components/StreamingMessage.tsx` - Streaming text component
- `frontend/src/components/StreamingMessage.test.tsx` - Component tests

**Modified Files:**
- `frontend/src/App.tsx` - Integrate useWebSocket
- `frontend/src/components/ChatContainer.tsx` - Use WebSocket props
- `frontend/src/components/telemetry/TelemetryPanel.tsx` - Real-time events

**Files to delete (Story 010):**
- `frontend/src/services/chatApi.ts` - REST client (deprecated)
- `frontend/src/services/telemetryApi.ts` - REST polling (deprecated)

### Tech Stack
[Source: Epic 003, Section "Tech Stack"]

- **React 18:** Hooks (useState, useEffect, useRef)
- **TypeScript:** Type-safe props
- **TailwindCSS:** Styling (existing design system)
- **shadcn/ui:** UI components (existing)
- **Lucide React:** Icons (existing)

**No new external dependencies required**

### Testing

#### Test File Locations
- Component tests: `frontend/src/components/*.test.tsx`
- Follow existing test pattern from Epic 002

#### Testing Standards
[Source: Epic 003, Section "Testing Strategy"]

**Component Test Requirements:**
```typescript
// StreamingMessage.test.tsx
- Test character-by-character rendering
- Test completion callback fires
- Test skip on click
- Test aria-label contains full content

// ChatContainer.test.tsx (updated)
- Mock useWebSocket hook
- Test sendMessage called on submit
- Test messages render correctly
- Test streaming vs non-streaming rendering
- Test input disabled when disconnected

// TelemetryPanel.test.tsx (updated)
- Remove polling tests
- Test telemetryEvents render
- Test event visual distinction (colors)
- Test auto-scroll behavior

// App.test.tsx (updated)
- Mock useWebSocket hook
- Test ConnectionStatus rendered
- Test error banner shown if error
- Test props passed correctly to children
```

**Testing Frameworks:**
- `vitest` or `jest` - Test runner
- `@testing-library/react` - Component testing
- `@testing-library/user-event` - User interaction testing

**Run Tests:**
```bash
npm test
npm run test:coverage
```

#### Accessibility Testing
[Source: Epic 003, Section "Accessibility Compliance"]

**Tools:**
- **axe DevTools:** Browser extension for automated accessibility scanning
- **Lighthouse:** Chrome DevTools audit
- **Screen Readers:** VoiceOver (Mac), NVDA (Windows)

**Requirements:**
- Lighthouse Accessibility score ≥ 90
- axe DevTools: 0 critical violations
- WCAG 2.1 AA compliance maintained (from Story 004)

**Test Checklist:**
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Screen reader announces new messages
- [ ] aria-live regions for dynamic content
- [ ] Color contrast meets WCAG AA (4.5:1 for text)
- [ ] Focus indicators visible
- [ ] Interactive elements have accessible names

### Technical Constraints
[Source: Epic 003, Section "Key Architectural Decisions"]

1. **Maintain UX flow** - Same user experience as Epic 002, just real-time
2. **No polling** - Remove all REST polling logic (5-second intervals)
3. **Smooth streaming** - No janky animations, 60fps target
4. **Accessibility first** - Screen readers get full text immediately
5. **Backward compatible** - Graceful degradation if WebSocket fails

### Performance Considerations
- StreamingMessage animation should be smooth (requestAnimationFrame if needed)
- Auto-scroll should be smooth, not jarring
- Large telemetry event lists should virtualize (if >500 events, use react-window)
- Message rendering should not block UI thread

### Regression Testing
[Source: Epic 003, Section "Definition of Done"]

- All existing tests must pass (no regressions)
- POST `/patient` endpoint must work (unaffected by WebSocket changes)
- Accessibility compliance maintained from Story 004
- Visual design unchanged (only internal implementation changed)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-20 | 1.0 | Initial story creation | Bob (Scrum Master) |

## Dev Agent Record

### Agent Model Used
_To be filled by Dev Agent during implementation_

### Debug Log References
_To be filled by Dev Agent during implementation_

### Completion Notes
_To be filled by Dev Agent during implementation_

### File List
_To be filled by Dev Agent during implementation_

## QA Results
_To be filled by QA Agent after implementation_
