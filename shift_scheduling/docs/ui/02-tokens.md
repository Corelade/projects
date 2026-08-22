# 02 — Tokens

**This file is the contract.** It maps 1:1 to `web/src/styles/theme.css`. If a
value appears in the code that isn't here, that's drift.

---

## The rule

> No colour, font size, spacing value, radius, shadow or z-index is written
> literally anywhere except `theme.css`.

That applies to **all three** places styles can appear:

| Where | Allowed | Not allowed |
|---|---|---|
| Tailwind utility classes | `bg-surface`, `text-fg`, `border-border` | `bg-[#f8fafc]`, `text-[13px]`, `p-[7px]` |
| Component / page `.css` | `color: var(--color-fg)` | `color: #0f172a` |
| Inline `style` | token vars only, and only for computed values | any literal |

Page-specific CSS files are explicitly permitted — `pages/schedule/schedule.css`
holds the rota grid's sticky-column and grid-template rules, which Tailwind
utilities express poorly. They still consume `var(--…)`.

---

## Tailwind v4 wiring

Tailwind v4 is CSS-first: tokens declared in `@theme` become utilities
automatically. `--color-brand-600` generates `bg-brand-600`, `text-brand-600`,
`border-brand-600` — and remains readable as `var(--color-brand-600)` inside a
plain `.css` file. One declaration, both consumption styles.

```css
/* web/src/styles/theme.css */
@import "tailwindcss";

@theme {
  --color-brand-600: #4f46e5;
  /* … */
}
```

---

## Colour tokens

### Semantic aliases — prefer these in components

Components reference *roles*, not raw ramp steps. Swapping the palette then
touches one block.

| Token | Value | Meaning |
|---|---|---|
| `--color-bg` | slate-50 | page background |
| `--color-surface` | `#ffffff` | card, table, drawer surface |
| `--color-surface-subtle` | slate-100 | zebra rows, hover, inset panels |
| `--color-border` | slate-200 | default border |
| `--color-border-strong` | slate-300 | emphasised / disabled border |
| `--color-fg` | slate-900 | primary text |
| `--color-fg-muted` | slate-500 | secondary text |
| `--color-fg-subtle` | slate-400 | placeholder, disabled text |
| `--color-fg-inverse` | `#ffffff` | text on brand/dark fills |

### Ramps

```css
--color-slate-50:  #f8fafc;   --color-slate-500: #64748b;
--color-slate-100: #f1f5f9;   --color-slate-600: #475569;
--color-slate-200: #e2e8f0;   --color-slate-700: #334155;
--color-slate-300: #cbd5e1;   --color-slate-800: #1e293b;
--color-slate-400: #94a3b8;   --color-slate-900: #0f172a;
                              --color-slate-950: #020617;

--color-brand-50:  #eef2ff;   --color-brand-500: #6366f1;
--color-brand-100: #e0e7ff;   --color-brand-600: #4f46e5;
--color-brand-200: #c7d2fe;   --color-brand-700: #4338ca;
                              --color-brand-800: #3730a3;
```

### Semantic states

```css
--color-success-50: #ecfdf5;  --color-success-200: #a7f3d0;
--color-success-600: #059669; --color-success-700: #047857;

--color-warning-50: #fffbeb;  --color-warning-200: #fde68a;
--color-warning-600: #d97706; --color-warning-700: #b45309;

--color-danger-50: #fff1f2;   --color-danger-200: #fecdd3;
--color-danger-600: #e11d48;  --color-danger-700: #be123c;

--color-info-50: #f0f9ff;     --color-info-200: #bae6fd;
--color-info-600: #0284c7;    --color-info-700: #0369a1;
```

### Shift identity

```css
--color-shift-morning-bg:     #fffbeb;
--color-shift-morning-border: #fde68a;
--color-shift-morning-fg:     #b45309;

--color-shift-afternoon-bg:     #f0f9ff;
--color-shift-afternoon-border: #bae6fd;
--color-shift-afternoon-fg:     #0369a1;

--color-shift-evening-bg:     #f5f3ff;
--color-shift-evening-border: #ddd6fe;
--color-shift-evening-fg:     #6d28d9;
```

### Coverage

```css
--color-coverage-under-bg:     var(--color-danger-50);
--color-coverage-under-border: var(--color-danger-200);
--color-coverage-at-min-bg:    var(--color-warning-50);
--color-coverage-empty-bg:     var(--color-slate-50);
```

### Overlays

```css
--color-backdrop: rgb(15 23 42 / 0.3);   /* drawer + modal scrim */
--color-shimmer:  rgb(255 255 255 / 0.6); /* skeleton sweep      */
```

### Print ink

Paper is always black on white regardless of theme, but it still goes through
tokens so the drift grep stays absolute — no literal ever escapes `theme.css`.

```css
--color-print-ink:   #000;
--color-print-paper: #fff;
```

---

## Typography tokens

```css
--font-sans: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI",
             Roboto, Helvetica, Arial, sans-serif;

--text-display: 1.875rem;  --text-display--line-height: 2.25rem;
--text-h1:      1.5rem;    --text-h1--line-height:      2rem;
--text-h2:      1.25rem;   --text-h2--line-height:      1.75rem;
--text-h3:      1rem;      --text-h3--line-height:      1.5rem;
--text-body:    0.875rem;  --text-body--line-height:    1.25rem;
--text-small:   0.8125rem; --text-small--line-height:   1.125rem;
--text-caption: 0.75rem;   --text-caption--line-height: 1rem;

--font-weight-normal:   400;
--font-weight-medium:   500;
--font-weight-semibold: 600;

--tracking-caption: 0.04em;
```

---

## Spacing, sizing, radius, shadow

Spacing uses Tailwind's default 4px scale — not re-declared. Named metrics that
recur:

```css
--size-row:           3rem;    /* 48px table row      */
--size-row-header:    2.5rem;  /* 40px table header   */
--size-control:       2.5rem;  /* 40px input, button  */
--size-control-sm:    2rem;    /* 32px small button   */
--size-topbar:        4rem;    /* 64px                */
--size-sidebar:      16.25rem; /* 260px               */
--size-rota-cell-min: 3.5rem;  /* 56px                */
--size-drawer:       30rem;    /* 480px drawer width  */

--radius-sm: 0.25rem;   /* 4px  */
--radius-md: 0.375rem;  /* 6px — default */
--radius-lg: 0.5rem;    /* 8px  */

--shadow-xs: 0 1px 2px rgb(15 23 42 / 0.04);
--shadow-sm: 0 1px 3px rgb(15 23 42 / 0.08), 0 1px 2px rgb(15 23 42 / 0.04);
--shadow-md: 0 10px 24px rgb(15 23 42 / 0.10);

--ring-focus-color:  var(--color-brand-500);
--ring-focus-width:  2px;
--ring-focus-offset: 2px;
```

---

## Motion and layering

```css
--duration-fast: 120ms;
--duration-base: 200ms;
--duration-slow: 280ms;
--ease-out:   cubic-bezier(0, 0, 0.2, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);

--z-base: 0;  --z-sticky: 10;  --z-dropdown: 20;
--z-backdrop: 30;  --z-overlay: 40;  --z-toast: 50;
```

---

## Dark mode (not built)

Tokens are structured so a future dark mode redefines only the **semantic
aliases** — `--color-bg`, `--color-surface`, `--color-fg`, `--color-border` and
the shift/coverage backgrounds — under `@media (prefers-color-scheme: dark)`.
The ramps stay put. Nothing in this pass should hard-code a light-mode
assumption that would block that, e.g. `text-slate-900` where `text-fg` would do.

---
*Changelog:*
*2026-08-21 — initial.*
*2026-08-21 — added overlay, print-ink and `--size-drawer` tokens; split
`--ring-focus` into `-color` / `-width` / `-offset` so the `@utility focus-ring`
rule can consume them individually. Found by the Phase 9 token-parity audit.*
