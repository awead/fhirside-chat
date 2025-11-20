# Accessibility Checklist - FHIRside Chat

WCAG 2.1 Level AA compliance checklist for the FHIRside Chat interface.

## Pre-Implementation Checklist

Use this checklist during Story 004 (Chat UI Enhancement) and Story 005 (Telemetry Panel).

---

## 1. Perceivable

### 1.1 Text Alternatives

- [ ] All icons have appropriate `aria-label` attributes
- [ ] Images (if any) have meaningful `alt` text
- [ ] Loading spinners have `aria-label="Loading"` or equivalent
- [ ] Send button has text or `aria-label="Send message"`
- [ ] New Session button has text or `aria-label="Start new session"`
- [ ] Collapse/expand buttons have `aria-label` indicating state

**Example:**
```tsx
<button aria-label="Send message">
  <Send className="w-5 h-5" />
</button>

<button aria-label={isExpanded ? "Collapse panel" : "Expand panel"}>
  {isExpanded ? <ChevronUp /> : <ChevronDown />}
</button>
```

### 1.2 Time-based Media

- [ ] N/A - No video or audio content

### 1.3 Adaptable

- [ ] Content structure uses semantic HTML (`<header>`, `<main>`, `<aside>`, `<nav>`)
- [ ] Message list uses `<ul>` and `<li>` for proper list semantics
- [ ] Heading hierarchy is logical (h1 → h2 → h3, no skips)
- [ ] Chat input uses proper `<form>` element
- [ ] Input field has associated `<label>` (visible or `aria-label`)
- [ ] Telemetry panel uses appropriate ARIA landmarks

**Example:**
```tsx
<main role="main" aria-label="Chat interface">
  <div className="chat-container">
    <ul role="list" aria-label="Message history">
      <li role="listitem">...</li>
    </ul>
  </div>
</main>

<aside role="complementary" aria-label="Telemetry panel">
  <h2>Telemetry</h2>
  ...
</aside>
```

### 1.4 Distinguishable

#### Color Contrast
- [ ] User message text (white on blue #3b82f6): 4.5:1 ✓
- [ ] Assistant message text (dark on gray #f3f4f6): 12:1 ✓
- [ ] Button text: ≥ 4.5:1 ratio
- [ ] Error messages: ≥ 4.5:1 ratio
- [ ] Link text: ≥ 4.5:1 ratio
- [ ] OpenAI span border (#8b5cf6): Decorative, not relied on alone
- [ ] MCP span border (#3b82f6): Decorative, not relied on alone

**Verification:** Use WebAIM Contrast Checker or browser DevTools

#### Color Is Not Only Method
- [ ] OpenAI spans distinguished by: border + icon + text label
- [ ] MCP spans distinguished by: border + icon + text label
- [ ] Error states use: color + icon + text
- [ ] Success states use: color + icon + text
- [ ] Loading states use: animation + text
- [ ] Focus indicators visible without relying on color alone

#### Text Resize
- [ ] Text remains readable when zoomed to 200%
- [ ] Layout does not break at 200% zoom
- [ ] No horizontal scrolling required at 200% zoom (mobile exempt)
- [ ] Font sizes use relative units (rem, em) not pixels

#### Images of Text
- [ ] No images of text used (N/A for this project)

---

## 2. Operable

### 2.1 Keyboard Accessible

#### Keyboard Navigation
- [ ] All interactive elements accessible via Tab key
- [ ] Tab order is logical (top to bottom, left to right)
- [ ] Send button activatable with Enter or Space
- [ ] Message input submits on Enter key press
- [ ] Telemetry panel collapsible with Enter/Space
- [ ] Span expand/collapse with Enter/Space
- [ ] New Session button accessible via keyboard
- [ ] No keyboard traps (can Tab out of all components)

**Test:** Navigate entire interface using only keyboard

#### Skip Links
- [ ] "Skip to main content" link at page top (optional but recommended)
- [ ] Skip link becomes visible on focus

**Example:**
```tsx
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:p-4"
>
  Skip to main content
</a>
```

### 2.2 Enough Time

- [ ] No time limits on user actions (N/A)
- [ ] Auto-refresh can be paused/stopped (✓ has toggle)
- [ ] Auto-refresh interval is configurable (✓ in settings)

### 2.3 Seizures and Physical Reactions

- [ ] No flashing content
- [ ] Loading animations are subtle (< 3 flashes per second)
- [ ] Typing indicator animation is smooth, non-jarring

### 2.4 Navigable

#### Page Title
- [ ] Page has descriptive `<title>`: "FHIRside Chat - AI FHIR Assistant"

#### Focus Order
- [ ] Focus order matches visual order
- [ ] Focus moves logically through: header → chat → input → telemetry panel

#### Link Purpose
- [ ] All links have descriptive text or `aria-label`
- [ ] "New Session" button clearly indicates purpose

#### Focus Visible
- [ ] All focusable elements have visible focus indicator
- [ ] Focus ring is ≥ 2px and offset from element
- [ ] Focus ring color contrasts with background (3:1 minimum)

**Example:**
```css
/* Tailwind utility */
focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
```

#### Headings and Labels
- [ ] Page sections have headings (Chat, Telemetry)
- [ ] Form inputs have labels
- [ ] Buttons have descriptive text

**Example:**
```tsx
<label htmlFor="message-input" className="sr-only">
  Type your message
</label>
<input id="message-input" type="text" placeholder="Type a message..." />
```

---

## 3. Understandable

### 3.1 Readable

#### Language
- [ ] HTML lang attribute set: `<html lang="en">`
- [ ] Any non-English content has `lang` attribute

### 3.2 Predictable

#### On Focus
- [ ] Focus does not trigger unexpected actions
- [ ] Expanding span does not move focus unexpectedly

#### On Input
- [ ] Typing in input field does not auto-submit
- [ ] Form submits only on explicit action (Send button or Enter key)

#### Consistent Navigation
- [ ] Header remains consistent across states
- [ ] Button positions don't change
- [ ] Panel locations predictable

#### Consistent Identification
- [ ] Icons used consistently (same icon = same action)
- [ ] Button styles consistent
- [ ] Span types consistently indicated

### 3.3 Input Assistance

#### Error Identification
- [ ] Error messages are clearly visible
- [ ] Error messages describe the problem
- [ ] Error messages suggest how to fix
- [ ] Error states have `role="alert"` for screen readers

**Example:**
```tsx
<div role="alert" className="text-red-500 flex items-center gap-2">
  <AlertCircle className="w-5 h-5" />
  <span>Failed to send message. Please try again.</span>
</div>
```

#### Labels or Instructions
- [ ] Input field has placeholder text
- [ ] Empty states provide instructions
- [ ] Complex interactions have helper text

#### Error Prevention
- [ ] User can confirm before clearing session (optional)
- [ ] Draft message not lost on page reload (Story 003 excludes this)

---

## 4. Robust

### 4.1 Compatible

#### Parsing (HTML Validity)
- [ ] No duplicate IDs
- [ ] Elements have complete start and end tags
- [ ] Elements are properly nested
- [ ] Attributes are properly formed

**Verification:** Use W3C HTML Validator

#### Name, Role, Value
- [ ] All custom components have proper ARIA roles
- [ ] Interactive elements have accessible names
- [ ] States are communicated to assistive tech

**Example:**
```tsx
<button
  aria-expanded={isExpanded}
  aria-controls="span-detail-123"
>
  {isExpanded ? 'Collapse' : 'Expand'}
</button>

<div id="span-detail-123" hidden={!isExpanded}>
  {/* Span details */}
</div>
```

---

## Testing Checklist

### Automated Testing

- [ ] Run axe DevTools in browser (0 violations target)
- [ ] Run Lighthouse Accessibility audit (≥ 90 score)
- [ ] Run WAVE browser extension
- [ ] Run eslint-plugin-jsx-a11y (if using ESLint)

### Manual Testing

#### Keyboard Navigation
- [ ] Tab through entire interface (logical order)
- [ ] Enter/Space activate all buttons
- [ ] Arrow keys work in lists (if implemented)
- [ ] Esc closes modals/drawers (if applicable)

#### Screen Reader Testing

**Test with at least one screen reader:**
- [ ] VoiceOver (Mac): Cmd + F5
- [ ] NVDA (Windows): Free download
- [ ] JAWS (Windows): Trial version

**Verify:**
- [ ] All content is announced
- [ ] Button purposes are clear
- [ ] Form labels are associated
- [ ] Error messages are announced
- [ ] Loading states are announced
- [ ] Focus changes are communicated

#### Zoom Testing
- [ ] Interface works at 200% zoom
- [ ] Text remains readable
- [ ] No overlapping content
- [ ] All functionality available

#### Mobile Accessibility
- [ ] Touch targets ≥ 44x44px
- [ ] Swipe gestures have keyboard alternatives
- [ ] Pinch zoom not disabled
- [ ] Content readable without horizontal scroll

---

## ARIA Attributes Reference

### Common Patterns

#### Collapsible Panel
```tsx
<button
  aria-expanded={isOpen}
  aria-controls="panel-id"
  onClick={toggle}
>
  {isOpen ? 'Collapse' : 'Expand'}
</button>
<div id="panel-id" hidden={!isOpen}>
  {/* Content */}
</div>
```

#### Live Region (for dynamic content)
```tsx
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>
```

#### Loading Spinner
```tsx
<div role="status" aria-live="polite">
  <Loader2 className="animate-spin" />
  <span className="sr-only">Loading traces...</span>
</div>
```

#### Alert (for errors)
```tsx
<div role="alert" className="error-message">
  Failed to send message
</div>
```

#### Landmark Regions
```tsx
<header role="banner">
  {/* Site header */}
</header>

<main role="main">
  {/* Primary content */}
</main>

<aside role="complementary">
  {/* Telemetry panel */}
</aside>
```

---

## Screen Reader Only Text

Use for visual icons that need text alternatives:

```css
/* Tailwind: sr-only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Visible on focus (for skip links) */
.sr-only:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

**Example Usage:**
```tsx
<button>
  <Send className="w-5 h-5" />
  <span className="sr-only">Send message</span>
</button>
```

---

## Acceptance Criteria Mapping

These checklist items map to Story 004 and Story 005 acceptance criteria:

### Story 004 (Chat UI Enhancement)
- Section 6: Accessibility Enhancements (AC 67-79)

### Story 005 (Telemetry Panel)
- Telemetry Panel Component (AC 27-28): ARIA labels, keyboard access
- Span List Display (AC 43-45): Visual distinction, contrast, icon visibility
- Performance (implicit): No UI freezing affects accessibility

---

## Resources

### Testing Tools
- **axe DevTools:** https://www.deque.com/axe/devtools/
- **Lighthouse:** Built into Chrome DevTools
- **WAVE:** https://wave.webaim.org/extension/
- **Contrast Checker:** https://webaim.org/resources/contrastchecker/

### Guidelines
- **WCAG 2.1:** https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA Authoring Practices:** https://www.w3.org/WAI/ARIA/apg/

### Screen Readers
- **VoiceOver (Mac):** Built-in, Cmd + F5
- **NVDA (Windows):** https://www.nvaccess.org/download/
- **JAWS (Windows):** https://www.freedomscientific.com/products/software/jaws/

---

## Definition of Done

Story 004 and Story 005 are **not complete** until:
- [ ] All applicable checklist items pass
- [ ] axe DevTools reports 0 violations
- [ ] Lighthouse Accessibility score ≥ 90
- [ ] Manual keyboard navigation works
- [ ] Manual screen reader test passes
- [ ] Manual zoom test (200%) passes
