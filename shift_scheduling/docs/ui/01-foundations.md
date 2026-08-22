# 01 — Foundations

Values here are the *rationale*. The machine-readable list lives in
`02-tokens.md`, which maps 1:1 to `web/src/styles/theme.css`.

---

## Colour

### Neutrals — slate

The canvas. Chosen over pure grey because the faint blue cast sits better
against the indigo accent and reads less clinical on white.

| Step | Hex | Use |
|---|---|---|
| 50 | `#f8fafc` | page background |
| 100 | `#f1f5f9` | subtle fills, table zebra, hover |
| 200 | `#e2e8f0` | **default border** |
| 300 | `#cbd5e1` | strong border, disabled border |
| 400 | `#94a3b8` | placeholder, disabled text, icons at rest |
| 500 | `#64748b` | secondary text |
| 600 | `#475569` | body text on tinted surfaces |
| 700 | `#334155` | strong body text |
| 800 | `#1e293b` | headings |
| 900 | `#0f172a` | **primary text** |
| 950 | `#020617` | reserved (dark mode surface) |

Surfaces are white `#ffffff`; the page behind them is slate-50. Cards lift by
border + shadow, not by being lighter than the page.

### Brand — indigo

One accent, used sparingly: primary buttons, active nav, focus rings, links,
selected chips. If everything is indigo nothing is.

| Step | Hex | Use |
|---|---|---|
| 50 | `#eef2ff` | selected row, subtle accent fill |
| 100 | `#e0e7ff` | chip selected background |
| 200 | `#c7d2fe` | accent border |
| 500 | `#6366f1` | focus ring |
| 600 | `#4f46e5` | **primary action** |
| 700 | `#4338ca` | primary hover |
| 800 | `#3730a3` | primary active/pressed |

### Semantic

| Role | Colour | 50 | 200 | 600 | 700 |
|---|---|---|---|---|---|
| success | emerald | `#ecfdf5` | `#a7f3d0` | `#059669` | `#047857` |
| warning | amber | `#fffbeb` | `#fde68a` | `#d97706` | `#b45309` |
| danger | rose | `#fff1f2` | `#fecdd3` | `#e11d48` | `#be123c` |
| info | sky | `#f0f9ff` | `#bae6fd` | `#0284c7` | `#0369a1` |

### Shift identity

Drives the rota grid. Three hues that stay distinguishable in greyscale because
their lightness differs, and that are *never the only* signal — every cell also
carries its shift name.

| Shift | Hue | bg (50) | border (200) | text (700) | Greyscale |
|---|---|---|---|---|---|
| Morning | amber | `#fffbeb` | `#fde68a` | `#b45309` | lightest |
| Afternoon | sky | `#f0f9ff` | `#bae6fd` | `#0369a1` | mid |
| Evening | violet | `#f5f3ff` | `#ddd6fe` | `#6d28d9` | darkest |

The progression light → dark mirrors the progression of the day, which makes it
learnable rather than arbitrary.

### Coverage state

Applied to a rota cell based on headcount vs the department's `min_staff`.

| State | Treatment | Non-colour signal |
|---|---|---|
| Below minimum | rose-50 fill, rose-200 border | ⚠ icon + count `1/2` |
| At minimum | amber-50 fill | count `2/2` |
| At or above target | no fill | count only |
| Empty cell | slate-50 fill, dashed border | em dash `—` |

---

## Typography

**Inter**, one family, loaded from Google Fonts with a system fallback stack.
Chosen for its large x-height and unambiguous `1` / `l` / `I` — it stays legible
at 13–14px, which is where this UI lives.

```
font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI",
             Roboto, Helvetica, Arial, sans-serif;
```

**All numbers use `font-variant-numeric: tabular-nums`** — hours, headcounts,
dates and the rota grid. Proportional digits make columns of numbers jitter.

| Token | Size / line-height | Weight | Use |
|---|---|---|---|
| `display` | 30 / 36 | 600 | page hero |
| `h1` | 24 / 32 | 600 | page title |
| `h2` | 20 / 28 | 600 | section heading |
| `h3` | 16 / 24 | 600 | card / panel header |
| `body` | 14 / 20 | 400 | **default** |
| `body-strong` | 14 / 20 | 500 | emphasised body, table cell key |
| `small` | 13 / 18 | 400 | hints, helper text, meta |
| `caption` | 12 / 16 | 500, `+0.04em`, uppercase | table headers, field labels |

Line length in prose blocks caps at `65ch`. Tables and the rota grid are exempt.

---

## Spacing

4px base. Tailwind's default scale (`1`=4, `2`=8, `3`=12, `4`=16, `6`=24,
`8`=32, `12`=48). Never an arbitrary value.

| Context | Value |
|---|---|
| Field label → input | 6px |
| Between fields in a form | 16px |
| Between form sections | 24px |
| Card padding | 20px |
| Page padding | 24px |
| Table cell padding | 12px 16px |
| Icon → adjacent text | 8px |

**Density metrics**

| Element | Height |
|---|---|
| Table row | 48px |
| Table header row | 40px |
| Input / select | 40px |
| Button (md) | 40px |
| Button (sm) | 32px |
| Topbar | 64px |
| Sidebar width | 260px |
| Rota cell min-height | 56px |

---

## Radius, border, shadow

**Radius** — sm `4px` (chips, badges), **md `6px` (default: buttons, inputs,
cards)**, lg `8px` (modals, drawers), full (avatars, pills).

**Border** — `1px solid slate-200` everywhere by default. The previous UI used
2px borders throughout, which made every table read as a spreadsheet grid and
fought with the content. Weight is earned, not default.

**Shadow** — three steps, slate-tinted rather than pure black so they don't
muddy against the blue-grey canvas.

| Token | Value | Use |
|---|---|---|
| `xs` | `0 1px 2px rgb(15 23 42 / 0.04)` | cards at rest |
| `sm` | `0 1px 3px rgb(15 23 42 / 0.08), 0 1px 2px rgb(15 23 42 / 0.04)` | dropdowns, popovers |
| `md` | `0 10px 24px rgb(15 23 42 / 0.10)` | modals, drawers |

---

## Focus

Every interactive element shows a visible focus ring on `:focus-visible`:

```
outline: 2px solid var(--color-brand-500);
outline-offset: 2px;
```

Never `outline: none` without a replacement. Focus is not decoration.

---

## Icons

Heroicons outline, 24×24 viewBox, `stroke-width: 1.5`, sized `16px` (inline)
or `20px` (standalone / buttons). `currentColor` only — icons inherit text
colour, never carry their own.

Every icon-only button has an `aria-label`.

---

## Motion

Fast and few. Motion confirms an action; it never announces itself.

| Token | Duration | Easing | Use |
|---|---|---|---|
| `fast` | 120ms | `ease-out` | hover, focus, chip toggle |
| `base` | 200ms | `ease-out` | dropdown, toast, tooltip |
| `slow` | 280ms | `cubic-bezier(.32,.72,0,1)` | drawer, modal |

All of it wrapped in `@media (prefers-reduced-motion: reduce)` → duration `0.01ms`.

Never animate a rota cell's contents on data refresh — it makes the grid feel
unstable.

---

## Z-index

Named steps only; no ad-hoc numbers.

| Layer | Value |
|---|---|
| base | 0 |
| sticky (table header, first column) | 10 |
| dropdown / popover | 20 |
| drawer & modal backdrop | 30 |
| drawer / modal | 40 |
| toast | 50 |

---
*Changelog: 2026-08-21 — initial.*
