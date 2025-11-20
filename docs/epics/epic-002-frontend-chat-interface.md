# Epic 002: Front-End Chat Interface with Telemetry - Brownfield Enhancement

**Status:** ✅ Complete
**Completion Date:** 2025-11-20

## Epic Goal

Provide users with an interactive web-based chat interface to communicate with the FHIRside Chat backend while visualizing real-time telemetry traces showing OpenAI API calls and Aidbox MCP server interactions.

## Epic Description

### Existing System Context

**Current relevant functionality:**
- FastAPI backend with `/chat` POST endpoint accepting `session_id` and `message`
- WebSocket endpoint at `/ws` for real-time chat (not used in v1)
- OpenTelemetry instrumentation sending traces to Jaeger (http://localhost:16686)
- PydanticAI agents making calls to Azure OpenAI and Aidbox FHIR server via MCP

**Technology stack:**
- Backend: Python 3.13, FastAPI, PydanticAI, OpenTelemetry
- Existing telemetry: Jaeger UI at localhost:16686
- No existing front-end (backend API only)

**Integration points:**
- REST API `/chat` endpoint (POST with JSON)
- OpenTelemetry OTLP exporter at http://localhost:4317
- Need to expose telemetry data to front-end via new API endpoint

### Enhancement Details

**What's being added/changed:**

1. **Web-based chat interface** - Single-page application with:
   - Chat input field and message history display
   - Session management (generate/reuse session IDs)
   - Modern, responsive UI following best UX practices

2. **Telemetry visualization panel** - Real-time display of:
   - OpenAI API calls (prompts, responses, token usage)
   - Aidbox MCP server queries and responses
   - Trace timing and span information
   - Error states and debugging information

3. **Backend telemetry API** - New endpoint to:
   - Query and expose OpenTelemetry trace data
   - Stream or poll traces for current chat session
   - Format trace data for front-end consumption

**How it integrates:**
- Front-end served as static assets (from `/static` or separate service)
- Calls existing `/chat` POST endpoint for message processing
- New `/telemetry` endpoint provides trace data for visualization
- WebSocket option for real-time trace streaming (optional for v1)

**Success criteria:**
- Users can send messages and see AI responses in a chat interface
- Telemetry panel shows OpenAI prompts/responses for each message
- Telemetry panel shows MCP queries to Aidbox server
- Trace data synchronized with corresponding chat messages
- UI is responsive and accessible on desktop browsers
- No degradation of existing API performance

## Stories

This epic has been broken down into four detailed, properly-scoped stories for iterative development.

### Story 002: Backend Telemetry API Endpoint

**File:** `docs/stories/story-002-telemetry-api-endpoint.md`
**Effort:** 3-5 Story Points (~7-8 hours)
**Status:** Ready for Development
**Dependencies:** None

Create a FastAPI endpoint that exposes OpenTelemetry trace data for front-end consumption. Includes telemetry data models, Jaeger query integration, CORS configuration, and session ID instrumentation.

**Key Deliverables:**
- `/telemetry/{session_id}` GET endpoint
- Telemetry data models (TypeScript-compatible)
- Jaeger Query API client
- Session ID added to OpenTelemetry spans
- CORS middleware for localhost origins

---

### Story 003: React Chat Foundation

**File:** `docs/stories/story-003-react-chat-foundation.md`
**Effort:** 3-5 Story Points (~5-6 hours)
**Status:** Ready for Development
**Dependencies:** Story 002 (for CORS configuration)

Set up Vite + React + TypeScript project with basic chat functionality. Minimal styling (no TailwindCSS yet). Focuses on functional chat with API integration and session management.

**Key Deliverables:**
- Vite + React + TypeScript project structure
- Basic chat UI components (functional, minimal styling)
- Session management with localStorage
- API integration with `/chat` endpoint
- Message history management
- Development workflow (npm scripts, hot reload)

---

### Story 004: Chat UI Enhancement

**File:** `docs/stories/story-004-chat-ui-enhancement.md`
**Effort:** 3-5 Story Points (~5-6 hours)
**Status:** Ready for Development
**Dependencies:** Story 003 (requires working chat UI)

Add professional styling with TailwindCSS, shadcn/ui components, Lucide icons, responsive design, and accessibility enhancements. Configure production build with FastAPI static file serving.

**Key Deliverables:**
- TailwindCSS configuration and styling
- shadcn/ui component integration
- Lucide React icons
- Responsive design (mobile/tablet/desktop)
- WCAG AA accessibility compliance
- Production build configuration
- FastAPI StaticFiles mount

---

### Story 005: Telemetry Visualization Panel

**File:** `docs/stories/story-005-telemetry-visualization-panel.md`
**Effort:** 5-8 Story Points (~8-10 hours)
**Status:** Ready for Development
**Dependencies:** Stories 002 (API), 003 (Chat UI), 004 (Styling)

Create developer-focused telemetry panel with syntax-highlighted span details, message-trace correlation, and multi-layer visual differentiation between OpenAI (purple) and MCP (blue) spans.

**Key Deliverables:**
- TelemetryPanel component (collapsible, responsive)
- SpanList with visual differentiation (OpenAI purple, MCP blue)
- SpanDetail with syntax highlighting and copy functionality
- Message-trace correlation with filtering
- Manual and auto-refresh controls
- Mobile-responsive bottom drawer
- Performance optimization (virtualization for 500+ spans)

---

## Design Artifacts

Comprehensive design documentation has been created to guide implementation:

### Tailwind Configuration (`docs/design/tailwind-config.md`)
Complete design system with:
- Custom color palette (OpenAI purple, MCP blue, semantic colors)
- Typography scale and font families
- Spacing system and responsive breakpoints
- Animation keyframes
- Usage examples and accessibility verification

### Wireframes (`docs/design/wireframes.md`)
ASCII wireframes for all layouts:
- Desktop split view (chat + telemetry side panel)
- Mobile layouts (chat-only and telemetry drawer)
- Expanded span details
- Message correlation states
- Loading and error states
- Component dimensions and specifications

### Accessibility Checklist (`docs/design/accessibility-checklist.md`)
WCAG 2.1 Level AA compliance guide:
- Complete 4-principle checklist (Perceivable, Operable, Understandable, Robust)
- ARIA patterns and examples
- Screen reader testing guide
- Color contrast specifications
- Testing tools and resources
- Mapped to Story 004 & 005 acceptance criteria

### Component Library (`docs/design/component-library.md`)
Complete component reference:
- Component hierarchy and interfaces
- TypeScript type definitions
- shadcn/ui component list
- Lucide React icon reference
- Usage examples and patterns
- Responsive behavior specifications
- Animation guidelines
- Testing examples

## Compatibility Requirements

- [x] Existing `/chat` API endpoint remains unchanged
- [x] Existing `/patient` API endpoint unaffected
- [x] No changes to existing telemetry instrumentation
- [x] Front-end is optional - API remains functional without it
- [x] Performance impact is minimal (telemetry queries are read-only)
- [x] CORS configuration added without breaking existing API consumers

## Risk Mitigation

**Primary Risk:** Exposing telemetry data (including OpenAI prompts/responses) to front-end could leak sensitive information

**Mitigation:**
- Telemetry endpoint only accessible on localhost development environment
- Add authentication/authorization before production deployment
- Filter sensitive data from traces (API keys, patient PHI)
- Document security considerations in README

**Secondary Risk:** Front-end build complexity adds overhead to development workflow

**Mitigation:**
- Use modern tooling (Vite) with hot reload for fast iteration
- Separate front-end and backend development concerns
- Document front-end setup in README
- Make front-end optional - backend remains usable via curl/Postman

**Rollback Plan:**
- Remove `/telemetry` endpoint if issues arise
- Revert static file serving configuration
- Backend `/chat` API continues to work independently

## Definition of Done

**All Stories Complete:**
- [x] Story 002: Backend Telemetry API Endpoint (with all acceptance criteria met)
- [x] Story 003: React Chat Foundation (with all acceptance criteria met)
- [x] Story 004: Chat UI Enhancement (with all acceptance criteria met)
- [x] Story 005: Telemetry Visualization Panel (with all acceptance criteria met)

**Functional Requirements:**
- [x] `/telemetry/{session_id}` API endpoint implemented and tested
- [x] Chat UI functional with message send/receive
- [x] Session management working (persists across reloads)
- [x] Telemetry panel displays OpenAI (purple) and MCP (blue) traces with clear visual distinction
- [x] Message-trace correlation working
- [x] Responsive design works on mobile, tablet, desktop

**Quality Requirements:**
- [x] All existing tests pass (no regressions)
- [x] New tests achieve 80%+ coverage for new code
- [x] Existing `/chat` endpoint verified through testing
- [x] Existing `/patient` endpoint verified through testing
- [x] Lighthouse Accessibility score ≥ 90
- [x] axe DevTools reports 0 critical violations
- [x] No performance degradation on existing API

**Documentation:**
- [x] README updated with front-end setup instructions
- [x] Front-end build process documented
- [x] Design artifacts available in `docs/design/`
- [x] Security considerations documented (telemetry data exposure)

**Integration Testing:**
- [x] Manual E2E test with real OpenAI and Aidbox
- [x] Chat conversation works end-to-end
- [x] Telemetry traces visible for each message
- [x] Auto-refresh updates traces correctly
- [x] Mobile responsive layout tested on actual devices

## Handoff Notes

### Story Details

All stories have been created with comprehensive detail:
- **Story 002:** Backend Telemetry API - 59 acceptance criteria, 6 tasks, ~7-8 hours
- **Story 003:** React Chat Foundation - 82 acceptance criteria, 6 tasks, ~5-6 hours
- **Story 004:** Chat UI Enhancement - 100 acceptance criteria, 8 tasks, ~5-6 hours
- **Story 005:** Telemetry Visualization Panel - 115 acceptance criteria, 9 tasks, ~8-10 hours

**Total Estimated Effort:** 25-30 hours across 4 stories

### Design Artifacts

Complete design system available in `docs/design/`:
- **tailwind-config.md** - Full Tailwind config with custom theme (copy directly to project)
- **wireframes.md** - ASCII wireframes for all screens and states
- **accessibility-checklist.md** - WCAG 2.1 AA compliance verification (use during Stories 004 & 005)
- **component-library.md** - Component reference with TypeScript interfaces and usage examples

### Development Sequence

**Recommended order:**
1. **Story 002** (Backend) - Foundation for telemetry, no frontend dependencies
2. **Story 003** (Chat Foundation) - Basic UI, functional but unstyled
3. **Story 004** (UI Enhancement) - Polish Story 003 with TailwindCSS/shadcn/ui
4. **Story 005** (Telemetry Panel) - Add developer telemetry visualization

**Parallel option:** Stories 003 and 002 can be developed in parallel by different team members.

### Technical Context

**Existing Patterns to Follow:**
- Async FastAPI endpoints with Pydantic models (`@app.get`, `@app.post`)
- OpenTelemetry instrumentation already in place via `instrumentation()`
- Standard error handling with `HTTPException`
- Environment-based configuration (API keys, endpoints)

**Key Integration Points:**
- `/chat` endpoint: `POST` with `ChatRequest` model (`session_id`, `message`)
- OpenTelemetry: Spans exported to Jaeger at localhost:4317
- Trace data: Query Jaeger Query API at localhost:16686/api/traces

**Critical Compatibility Requirements:**
- Must not modify existing `ChatService` or `chat_agent()` behavior
- CORS middleware added in Story 002 for front-end access (localhost origins)
- Static file serving configured in Story 004 using FastAPI's `StaticFiles`
- Session IDs must match between chat API and telemetry API
- Visual differentiation CRITICAL: OpenAI (purple) vs MCP (blue) spans

**Front-End Technology Stack (Confirmed):**
- **Framework:** React 18+ with Vite 5+
- **Language:** TypeScript (strict mode)
- **Styling:** TailwindCSS 3+ with custom design tokens
- **Components:** shadcn/ui (Button, Card, Input, ScrollArea, Sheet)
- **Icons:** Lucide React (Brain, Database, Send, etc.)
- **HTTP Client:** Fetch API (native, no axios)
- **Syntax Highlighting:** react-syntax-highlighter (for telemetry JSON)

Each story includes verification that existing `/chat` functionality remains intact.

## Success Metrics

**User Experience:**
- Users can have a conversation with the AI agent via web UI
- Developers can inspect trace data without switching to Jaeger UI
- Telemetry provides debugging value for understanding AI agent behavior

**Technical Quality:**
- Chat latency remains unchanged (< 5s for typical responses)
- Telemetry queries complete in < 1s
- No errors introduced in existing endpoints
- Code follows existing project style (ruff formatting, pytest tests)

**Documentation:**
- README updated with front-end setup instructions
- Telemetry endpoint documented in OpenAPI schema
- Security considerations documented for telemetry exposure
