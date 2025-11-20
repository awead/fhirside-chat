# Story: Telemetry Visualization Panel

**Status:** Ready for Development
**Story ID:** STORY-005
**Epic:** Epic 002 - Front-End Chat Interface with Telemetry
**Priority:** Medium
**Estimated Effort:** 5-8 Story Points
**Dependencies:** Story 002 (Telemetry API), Story 003 (React Chat Foundation), Story 004 (Chat UI Enhancement)

---

## Story

As a **developer debugging the FHIRside Chat system**,
I want **a telemetry panel that displays OpenAI API calls and Aidbox MCP queries in real-time**,
So that **I can understand what the AI agent is doing, troubleshoot issues, and verify correct behavior without switching to Jaeger UI**.

---

## Story Context

### Existing System Integration

- **Integrates with:** `/telemetry/{session_id}` API endpoint (Story 002), React chat UI (Story 003/004)
- **Technology:** React 18+, TypeScript, TailwindCSS, shadcn/ui, syntax highlighting
- **Follows pattern:** Developer tool panel pattern (collapsible, detailed view, technical data display)
- **Touch points:**
  - Telemetry API endpoint for fetching trace data
  - Session ID from chat application state
  - Chat message list for correlation
  - OpenTelemetry span format (from API response)

---

## Acceptance Criteria

### 1. Telemetry Data Models and API Integration

**Functional Requirements:**
1. Create TypeScript interfaces matching telemetry API response format
2. Implement `telemetryApi.ts` service for fetching trace data
3. Fetch telemetry data by session ID from `/telemetry/{session_id}` endpoint
4. Handle successful responses (200 OK with span data array)
5. Handle error responses (404, 500) gracefully
6. Parse span data into structured TypeScript objects

**Integration Requirements:**
7. Use Fetch API for GET requests to telemetry endpoint
8. TypeScript interfaces match backend `TelemetryResponse` model
9. API service returns typed responses with proper error handling
10. Telemetry fetching independent of chat message API calls

**Quality Requirements:**
11. TypeScript compilation passes with strict mode
12. API calls tested with real backend
13. Error handling tested with offline backend
14. Network errors display user-friendly messages

### 2. Telemetry Panel Component

**Functional Requirements:**
15. Create `TelemetryPanel` component with collapsible design
16. Toggle button to show/hide panel (default: visible)
17. Panel positioned adjacent to chat (split view or side panel)
18. Panel has header with title and collapse/expand control
19. Panel displays count of traces/spans for current session
20. Panel shows "No traces" state when session has no data

**Integration Requirements:**
21. Panel uses session ID from app state (shared with chat)
22. Panel styling matches chat UI (TailwindCSS + shadcn/ui)
23. Panel layout responsive (collapses to bottom drawer on mobile)
24. Panel state (collapsed/expanded) persists in localStorage

**Quality Requirements:**
25. Panel toggle animation is smooth (< 300ms)
26. Panel does not block chat interface when expanded
27. Panel accessible via keyboard (Tab, Enter to toggle)
28. Panel has proper ARIA labels for screen readers

### 3. Span List Display

**Functional Requirements:**
29. Create `SpanList` component to display list of traces
30. Display spans in chronological order (newest first or oldest first - configurable)
31. Each span shows: operation name, duration, timestamp, status (OK/ERROR)
32. Group spans by trace ID (show parent-child relationships if possible)
33. **CRITICAL:** Distinguish span types with multi-layer visual differentiation:
    - OpenAI spans: Purple accent (border-left: 4px solid #8b5cf6)
    - MCP/Aidbox spans: Blue accent (border-left: 4px solid #3b82f6)
    - Icons: Brain (OpenAI), Database (MCP)
    - Optional badges: [OpenAI] purple, [Aidbox] blue
34. Click on span to expand details

**Integration Requirements:**
35. Spans rendered as list of Card components with colored left border
36. Use Lucide React icons: `Brain` for OpenAI, `Database` for MCP
37. Status indicators: green checkmark for OK, red X for ERROR
38. Expandable/collapsible behavior for span details
39. Span type detected from operation_name field (e.g., "openai.*" vs "mcp.*")

**Quality Requirements:**
40. Span list renders performantly with 50+ spans
41. Spans load without blocking UI thread
42. Scroll behavior smooth with many spans
43. **Visual distinction between OpenAI and MCP spans is immediately obvious** (< 1 second recognition)
44. Color coding meets WCAG AA contrast requirements
45. Icons are clearly visible at all zoom levels

### 4. Span Detail View

**Functional Requirements:**
43. Create `SpanDetail` component for expanded span information
44. Display all span attributes: span_id, trace_id, parent_span_id
45. Display span timing: start_time, end_time, duration (formatted)
46. Display OpenAI-specific data: prompt, completion, model, token counts
47. Display MCP-specific data: FHIR query, resource type, response data
48. Display span status and any error messages
49. Syntax highlighting for JSON data (prompts, responses, queries)
50. Copyable text for prompt/response content (copy button)

**Integration Requirements:**
51. Use code block component for displaying JSON/text
52. Syntax highlighting with lightweight library (e.g., Prism or highlight.js)
53. Copy-to-clipboard functionality (native API or library)
54. Collapsible sections for long content (truncate with "Show more")

**Quality Requirements:**
55. Syntax highlighting renders correctly for JSON
56. Copy button provides user feedback (checkmark on success)
57. Long content (> 500 chars) is truncated with expand option
58. Rendering large JSON (> 10KB) does not freeze UI

### 5. Message-Trace Correlation

**Functional Requirements:**
59. Visually correlate traces with corresponding chat messages
60. Display trace count badge on each message (e.g., "3 traces")
61. Click on message to filter telemetry panel to that message's traces
62. Highlight active message when telemetry panel filtered
63. Clear filter button to show all traces again

**Integration Requirements:**
64. Use message timestamp to match with span timestamps
65. Store message-to-trace mapping in component state
66. Pass filter state between chat and telemetry components
67. Update telemetry panel when new message sent

**Quality Requirements:**
68. Correlation is accurate (< 1 second timestamp tolerance)
69. Filtering updates telemetry panel in < 100ms
70. Visual indication of active filter is clear
71. Correlation works for messages sent before panel loaded

### 6. Refresh and Auto-Refresh

**Functional Requirements:**
72. Manual refresh button to fetch latest traces
73. Auto-refresh toggle (on/off) with configurable interval
74. Auto-refresh interval: 5 seconds default, configurable to 10s/30s/60s
75. Loading indicator while fetching telemetry data
76. Timestamp showing when telemetry was last updated

**Integration Requirements:**
77. Use React useEffect hook for auto-refresh logic
78. Clear interval on component unmount (prevent memory leaks)
79. Pause auto-refresh when panel collapsed (optimization)
80. Resume auto-refresh when panel expanded

**Quality Requirements:**
81. Auto-refresh does not cause UI jank or flicker
82. Loading indicator is subtle (not disruptive)
83. Refresh interval preference persists in localStorage
84. Manual refresh works even when auto-refresh is on

### 7. Responsive Design and Mobile Support

**Functional Requirements:**
85. Telemetry panel adapts to screen size: desktop (side panel), mobile (bottom drawer)
86. On mobile, panel toggles from bottom sheet (slide up/down)
87. Span details truncate appropriately on narrow screens
88. Touch targets for collapse/expand are >= 44x44px

**Integration Requirements:**
89. Use Tailwind responsive classes for layout changes
90. Panel uses shadcn/ui Sheet component for mobile drawer
91. Test on mobile device emulation (320px - 768px widths)

**Quality Requirements:**
92. Layout does not break on any screen size
93. Panel remains usable on mobile devices
94. Swipe gestures work for mobile drawer (if using Sheet)
95. No horizontal scrolling on narrow screens

### 8. Performance Optimization

**Functional Requirements:**
96. Virtualize span list if > 100 spans (render only visible items)
97. Lazy load span details (don't render until expanded)
98. Debounce filter/search operations
99. Memoize expensive computations (span parsing, grouping)

**Integration Requirements:**
100. Use React.memo for span components to prevent re-renders
101. Use useMemo for span data transformations
102. Use useCallback for event handlers
103. Consider using react-window for virtualization if needed

**Quality Requirements:**
104. Rendering 100 spans takes < 500ms
105. Expanding span detail takes < 100ms
106. Filtering spans takes < 200ms
107. No performance degradation with 500+ spans

### 9. System Integration & Regression Testing

**Integration Requirements:**
108. Chat functionality from Stories 003/004 remains working
109. Telemetry API endpoint from Story 002 works correctly
110. Session management continues to function
111. No impact on backend performance

**Quality Requirements:**
112. All previous story tests pass
113. Manual E2E test: send message, view traces, correlate with message
114. Manual test: auto-refresh updates panel correctly
115. Manual test: panel works on mobile viewport

---

## Technical Notes

### Telemetry API TypeScript Interfaces

```typescript
// frontend/src/types/telemetry.ts
export interface SpanData {
  span_id: string;
  trace_id: string;
  parent_span_id?: string;
  operation_name: string;
  start_time: number; // Unix timestamp
  end_time: number;
  duration: number; // milliseconds
  attributes: SpanAttributes;
  status: 'OK' | 'ERROR';
  error_message?: string;
}

export interface SpanAttributes {
  // OpenAI attributes
  'openai.prompt'?: string;
  'openai.completion'?: string;
  'openai.model'?: string;
  'openai.token_count'?: number;

  // MCP attributes
  'mcp.query'?: string;
  'mcp.resource_type'?: string;
  'mcp.response'?: string;

  // Common
  session_id: string;
}

export interface TelemetryResponse {
  session_id: string;
  spans: SpanData[];
  trace_count: number;
}
```

### Component Structure

```
frontend/src/components/
├── telemetry/
│   ├── TelemetryPanel.tsx      # Main panel container
│   ├── SpanList.tsx            # List of spans
│   ├── SpanItem.tsx            # Individual span (collapsed)
│   ├── SpanDetail.tsx          # Expanded span details
│   ├── TraceCorrelation.tsx    # Message-trace correlation
│   └── RefreshControls.tsx     # Refresh and auto-refresh UI
```

### Visual Differentiation System

**CRITICAL REQUIREMENT:** OpenAI and MCP spans must be immediately distinguishable

```typescript
// Span type detection
function getSpanType(operationName: string): 'openai' | 'mcp' | 'unknown' {
  if (operationName.startsWith('openai.') || operationName.includes('OpenAI')) {
    return 'openai';
  }
  if (operationName.startsWith('mcp.') || operationName.includes('MCP') || operationName.includes('Aidbox')) {
    return 'mcp';
  }
  return 'unknown';
}

// Tailwind classes for span styling
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
  }
};
```

**Example SpanItem Component:**
```typescript
import { Brain, Database } from 'lucide-react';

function SpanItem({ span }: { span: SpanData }) {
  const type = getSpanType(span.operation_name);
  const styles = spanStyles[type];
  const Icon = styles.icon;

  return (
    <Card className={cn(
      'cursor-pointer transition-colors',
      styles.borderColor,
      styles.borderWidth,
      styles.hoverBg
    )}>
      <div className="flex items-center gap-3 p-3">
        <Icon className={cn('w-5 h-5', styles.iconColor)} />
        <span className="font-medium">{span.operation_name}</span>
        <span className="ml-auto text-sm text-gray-500">{span.duration}ms</span>
      </div>
    </Card>
  );
}
```

**Color Palette:**
```css
/* OpenAI spans - Purple theme */
--openai-border: #8b5cf6;     /* Purple 500 */
--openai-bg-hover: #f5f3ff;   /* Purple 50 */
--openai-badge-bg: #e9d5ff;   /* Purple 200 */
--openai-badge-text: #6b21a8; /* Purple 800 */

/* MCP/Aidbox spans - Blue theme */
--mcp-border: #3b82f6;        /* Blue 500 */
--mcp-bg-hover: #eff6ff;      /* Blue 50 */
--mcp-badge-bg: #bfdbfe;      /* Blue 200 */
--mcp-badge-text: #1e3a8a;    /* Blue 800 */
```

### Syntax Highlighting

Use lightweight syntax highlighter:
```bash
npm install react-syntax-highlighter @types/react-syntax-highlighter
```

```typescript
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

<SyntaxHighlighter language="json" style={vscDarkPlus}>
  {JSON.stringify(spanData, null, 2)}
</SyntaxHighlighter>
```

### Auto-Refresh Pattern

```typescript
// Auto-refresh hook
function useAutoRefresh(enabled: boolean, interval: number, callback: () => void) {
  useEffect(() => {
    if (!enabled) return;

    const intervalId = setInterval(callback, interval);
    return () => clearInterval(intervalId);
  }, [enabled, interval, callback]);
}
```

### Key Constraints

- **Developer Tool:** Focus on technical detail over visual polish
- **Performance:** Must handle 500+ spans without lag
- **Readability:** JSON data must be syntax-highlighted and formatted
- **Accessibility:** Keyboard navigation and screen reader support
- **Mobile:** Must work on mobile, but optimized for desktop use

---

## Definition of Done

- [x] Telemetry API integration functional with TypeScript types
- [x] TelemetryPanel component renders with collapse/expand
- [x] SpanList displays traces in chronological order
- [x] SpanDetail shows all span attributes with syntax highlighting
- [x] Message-trace correlation working with visual indicators
- [x] Manual refresh and auto-refresh functional
- [x] Responsive design works on mobile and desktop
- [x] Performance optimized for 500+ spans
- [x] Copy-to-clipboard works for span content
- [x] All Stories 002-004 functionality remains working
- [x] Manual E2E test: full workflow with telemetry inspection

---

## Risk and Compatibility Check

### Minimal Risk Assessment

**Primary Risk:** Large telemetry data (many spans) causes UI performance issues or memory leaks

**Mitigation:**
- Implement virtualization for span lists (> 100 spans)
- Lazy load span details (render on demand)
- Clear old spans when switching sessions
- Add span limit (e.g., only show last 1000 spans)
- Profile with React DevTools to identify bottlenecks

**Secondary Risk:** Syntax highlighting libraries increase bundle size significantly

**Mitigation:**
- Use lightweight highlighter (Prism lite build)
- Lazy load syntax highlighting library
- Code-split telemetry panel from main bundle
- Monitor bundle size and optimize if > 100KB added

**Rollback:** Disable telemetry panel feature (hide component), chat continues to work

### Compatibility Verification

- [x] No breaking changes to chat functionality
- [x] Telemetry API remains optional (works with/without frontend)
- [x] Session management unchanged
- [x] No backend code changes required

---

## Tasks

### Task 1: Create Telemetry Data Models and API Service
**Estimated Time:** 1 hour

#### Subtasks:
- [ ] Create `src/types/telemetry.ts` with span interfaces
- [ ] Create `src/services/telemetryApi.ts` for API calls
- [ ] Implement `fetchTelemetry(sessionId: string)` function
- [ ] Add error handling for API failures
- [ ] Write unit tests for API service
- [ ] Test with real backend endpoint

### Task 2: Build TelemetryPanel Component
**Estimated Time:** 1.5 hours

#### Subtasks:
- [ ] Create `src/components/telemetry/TelemetryPanel.tsx`
- [ ] Implement collapse/expand functionality
- [ ] Add toggle button with icon
- [ ] Style with TailwindCSS and shadcn/ui
- [ ] Add "No traces" empty state
- [ ] Store collapsed state in localStorage
- [ ] Test panel toggle behavior

### Task 3: Implement SpanList Component
**Estimated Time:** 2 hours

#### Subtasks:
- [ ] Create `src/components/telemetry/SpanList.tsx`
- [ ] Create `src/components/telemetry/SpanItem.tsx`
- [ ] Render list of spans with key information
- [ ] Add icons for span types (OpenAI, MCP)
- [ ] Add status indicators (OK, ERROR)
- [ ] Implement click to expand behavior
- [ ] Sort spans chronologically
- [ ] Test with mock span data

### Task 4: Build SpanDetail Component
**Estimated Time:** 2.5 hours

#### Subtasks:
- [ ] Create `src/components/telemetry/SpanDetail.tsx`
- [ ] Display all span attributes
- [ ] Format timestamps (human-readable)
- [ ] Install syntax highlighting library
- [ ] Add syntax highlighting for JSON data
- [ ] Implement copy-to-clipboard for content
- [ ] Add truncation for long content (> 500 chars)
- [ ] Test with OpenAI and MCP span examples

### Task 5: Implement Message-Trace Correlation
**Estimated Time:** 1.5 hours

#### Subtasks:
- [ ] Add trace count badge to Message component
- [ ] Implement timestamp matching logic
- [ ] Add click handler to filter traces by message
- [ ] Highlight active message when filter applied
- [ ] Add "Clear filter" button in telemetry panel
- [ ] Test correlation accuracy
- [ ] Test filter UI updates

### Task 6: Add Refresh Controls
**Estimated Time:** 1 hour

#### Subtasks:
- [ ] Create `src/components/telemetry/RefreshControls.tsx`
- [ ] Add manual refresh button
- [ ] Add auto-refresh toggle switch
- [ ] Add interval selector (5s/10s/30s/60s)
- [ ] Implement auto-refresh with useEffect
- [ ] Add last updated timestamp display
- [ ] Store refresh preferences in localStorage
- [ ] Test auto-refresh behavior

### Task 7: Responsive Design for Mobile
**Estimated Time:** 1 hour

#### Subtasks:
- [ ] Add responsive layout: side panel (desktop) → bottom drawer (mobile)
- [ ] Use shadcn/ui Sheet component for mobile drawer
- [ ] Test on mobile device emulation (320px - 768px)
- [ ] Ensure touch targets are adequate (>= 44px)
- [ ] Verify swipe gestures work for drawer
- [ ] Test span detail truncation on narrow screens

### Task 8: Performance Optimization
**Estimated Time:** 1.5 hours

#### Subtasks:
- [ ] Wrap span components with React.memo
- [ ] Use useMemo for span data processing
- [ ] Use useCallback for event handlers
- [ ] Implement virtualization if span count > 100 (react-window)
- [ ] Lazy load span details (render on expand only)
- [ ] Profile with React DevTools
- [ ] Test with 500+ spans dataset
- [ ] Optimize any performance bottlenecks

### Task 9: Integration and E2E Testing
**Estimated Time:** 1 hour

#### Subtasks:
- [ ] Integrate telemetry panel into main App layout
- [ ] Test full workflow: send message → view traces → correlate
- [ ] Test auto-refresh updates panel correctly
- [ ] Test responsive behavior on multiple screen sizes
- [ ] Test with real backend and Jaeger data
- [ ] Verify all previous story functionality still works
- [ ] Run accessibility audit (axe DevTools)
- [ ] Update README with telemetry panel usage

---

## Implementation Checkpoints

1. **After API integration:** Fetch traces successfully from endpoint
2. **After TelemetryPanel:** Panel renders and toggles correctly
3. **After SpanList:** Spans display in list with basic info
4. **After SpanDetail:** Can expand span and see all details with highlighting
5. **After correlation:** Click message, see filtered traces
6. **After refresh:** Manual and auto-refresh work correctly
7. **After responsive:** Works on mobile viewport
8. **After optimization:** Renders 500+ spans without lag
9. **Final:** Complete E2E workflow, all tests pass

---

## Dependencies and Sequencing

**Depends on:**
- Story 002 (Backend Telemetry API) - requires telemetry endpoint
- Story 003 (React Chat Foundation) - requires chat UI and session management
- Story 004 (Chat UI Enhancement) - uses same styling system

**Blocks:**
- None (this is the final story in Epic 002)

**Development Order:**
1. Data models and API service (foundation)
2. Telemetry panel structure (container)
3. Span list and item components (data display)
4. Span detail with syntax highlighting (detailed view)
5. Message-trace correlation (integration with chat)
6. Refresh controls (UX enhancement)
7. Responsive design (mobile support)
8. Performance optimization (handle scale)
9. Integration and testing (validation)

---

## Success Metrics

- Telemetry panel displays traces within 1 second of fetch
- Span list renders 500 spans in < 500ms
- Expanding span detail takes < 100ms
- Message-trace correlation accuracy >= 95%
- Auto-refresh does not cause UI flicker
- Bundle size increase < 150KB (with code splitting)
- Lighthouse Accessibility score >= 90
- Zero console errors during normal operation
- Developers can debug agent behavior without Jaeger UI
