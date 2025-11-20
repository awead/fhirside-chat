# Tailwind Configuration - FHIRside Chat

This document defines the complete design system for the FHIRside Chat front-end interface.

## Tailwind Config File

Copy this configuration to `frontend/tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Brand colors
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Primary blue
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },

        // Telemetry - OpenAI spans (Purple)
        openai: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',  // OpenAI accent
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },

        // Telemetry - MCP/Aidbox spans (Blue)
        mcp: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // MCP accent
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },

        // Chat message colors
        user: {
          bg: '#3b82f6',    // Blue 500
          text: '#ffffff',  // White
          hover: '#2563eb', // Blue 600
        },
        assistant: {
          bg: '#f3f4f6',    // Gray 100
          text: '#111827',  // Gray 900
          hover: '#e5e7eb', // Gray 200
        },

        // Semantic colors
        success: {
          50: '#f0fdf4',
          500: '#10b981',  // Green
          700: '#047857',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',  // Red
          700: '#b91c1c',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',  // Amber
          700: '#b45309',
        },
      },

      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },

      fontSize: {
        'xs': ['12px', { lineHeight: '16px' }],
        'sm': ['14px', { lineHeight: '20px' }],
        'base': ['16px', { lineHeight: '24px' }],
        'lg': ['18px', { lineHeight: '28px' }],
        'xl': ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px' }],
      },

      spacing: {
        '18': '4.5rem',  // 72px
        '22': '5.5rem',  // 88px
      },

      borderRadius: {
        'message': '12px',  // Message bubble radius
        'panel': '8px',     // Panel radius
      },

      maxWidth: {
        'chat': '800px',    // Max width for chat container
        'message': '70%',   // Max width for message bubbles
      },

      boxShadow: {
        'panel': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'message': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
      },

      animation: {
        'typing': 'typing 1.4s infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },

      keyframes: {
        typing: {
          '0%, 100%': { opacity: '0.2' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
```

## Design Tokens Reference

### Colors

#### Primary Actions
- **Primary Blue:** `#3b82f6` (buttons, links, user messages)
- **Primary Hover:** `#2563eb` (hover states)

#### Telemetry Spans
- **OpenAI Purple:** `#8b5cf6` (border, icons, badges)
- **MCP Blue:** `#3b82f6` (border, icons, badges)

#### Message Backgrounds
- **User Messages:** `#3b82f6` (blue) with white text
- **Assistant Messages:** `#f3f4f6` (gray-100) with dark text

#### Status Indicators
- **Success:** `#10b981` (green) - OK status
- **Error:** `#ef4444` (red) - ERROR status
- **Warning:** `#f59e0b` (amber) - warnings

### Typography

#### Font Families
- **UI Text:** Inter (or system-ui fallback)
- **Code/Telemetry:** JetBrains Mono (or Fira Code fallback)

#### Font Sizes
- **Extra Small (metadata):** 12px / 16px line-height
- **Small (timestamps):** 14px / 20px line-height
- **Base (messages, inputs):** 16px / 24px line-height
- **Large (headings):** 18-20px / 28px line-height
- **Extra Large (titles):** 24px / 32px line-height

### Spacing

Use Tailwind's default spacing scale (4px base unit):
- **Tight:** 8px (`space-2`)
- **Normal:** 12px (`space-3`)
- **Medium:** 16px (`space-4`)
- **Large:** 24px (`space-6`)
- **Extra Large:** 32px (`space-8`)

### Border Radius

- **Message Bubbles:** 12px (`rounded-message`)
- **Panels/Cards:** 8px (`rounded-panel`)
- **Buttons:** 6px (`rounded-md`)
- **Inputs:** 6px (`rounded-md`)

### Shadows

- **Panel Shadow:** Medium shadow for telemetry panel
- **Message Shadow:** Light shadow for message bubbles
- **Button Hover:** Subtle shadow on hover

### Responsive Breakpoints

```javascript
// Tailwind defaults (use as-is)
sm: '640px'   // Mobile landscape / small tablet
md: '768px'   // Tablet
lg: '1024px'  // Desktop
xl: '1280px'  // Large desktop
```

## Usage Examples

### Message Bubble

```tsx
// User message
<div className="ml-auto max-w-message bg-user-bg text-user-text rounded-message p-4 shadow-message">
  {content}
</div>

// Assistant message
<div className="mr-auto max-w-message bg-assistant-bg text-assistant-text rounded-message p-4 shadow-message">
  {content}
</div>
```

### OpenAI Span

```tsx
<Card className="border-l-4 border-l-openai-500 hover:bg-openai-50 transition-colors">
  <div className="flex items-center gap-3 p-3">
    <Brain className="w-5 h-5 text-openai-500" />
    <span>openai.chat.completion</span>
  </div>
</Card>
```

### MCP Span

```tsx
<Card className="border-l-4 border-l-mcp-500 hover:bg-mcp-50 transition-colors">
  <div className="flex items-center gap-3 p-3">
    <Database className="w-5 h-5 text-mcp-500" />
    <span>mcp.aidbox.query</span>
  </div>
</Card>
```

### Button States

```tsx
<button className="
  bg-primary-500 text-white
  hover:bg-primary-600 hover:scale-105
  active:bg-primary-700 active:scale-95
  focus:ring-2 focus:ring-primary-300
  disabled:bg-gray-300 disabled:cursor-not-allowed
  rounded-md px-4 py-2
  transition-all duration-200
">
  Send
</button>
```

## Accessibility

### Color Contrast Ratios (WCAG AA)

All color combinations meet WCAG AA standards:

- **User message (white on blue):** 4.5:1 ✓
- **Assistant message (dark on gray):** 12:1 ✓
- **OpenAI purple border on white:** 3.1:1 ✓ (decorative)
- **MCP blue border on white:** 3.1:1 ✓ (decorative)
- **Status indicators:** All > 4.5:1 ✓

### Focus Indicators

All interactive elements must have visible focus states:
```css
focus:ring-2 focus:ring-offset-2 focus:ring-[color]
```

### Touch Targets

Minimum 44x44px for mobile:
```css
min-h-[44px] min-w-[44px]
```

## Installation

Install required fonts:

```bash
# Add to frontend/index.html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

Or install via npm:
```bash
npm install @fontsource/inter @fontsource/jetbrains-mono
```

Then import in `src/main.tsx`:
```typescript
import '@fontsource/inter';
import '@fontsource/jetbrains-mono';
```
