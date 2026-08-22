# 03 — Components

## File convention

**One folder per component.** The folder is kebab-case, the files inside share
its name.

```
components/
  button/button.tsx
  toggle-chip/toggle-chip.tsx
  table/table.tsx
            table.css      ← only if Tailwind utilities can't express it
  navbar/navbar.tsx
```

A `.css` sibling appears **only** when the styling genuinely needs it — grid
templates, sticky positioning, `@container` queries, print rules, complex
pseudo-elements. Everything else is Tailwind utilities. Any `.css` file obeys
the token rule in `02-tokens.md`.

Every component exports a named type `XProps` alongside its default export.

## States every interactive component must implement

`default` · `hover` · `focus-visible` · `active` · `disabled` — plus `loading`
and `error` where they apply. A component is not done until all of its
applicable states exist. This list is what `08-drift-checklist.md` audits.

---

## Primitives

### `button/`
**Variants:** `primary` (brand-600 fill, white text) · `secondary` (white fill,
border) · `ghost` (transparent, hover surface-subtle) · `danger` (danger-600
fill).
**Sizes:** `sm` 32px · `md` 40px (default).
**Props:** `variant`, `size`, `loading`, `disabled`, `iconLeft`, `iconRight`,
`fullWidth`.
When `loading`: spinner replaces `iconLeft`, label stays, button is disabled.
Width must not change — reserve the icon slot.
Icon-only buttons require `aria-label`.

> Fixed from the old UI: its disabled state used a *darker* blue than the enabled
> state, reading as more prominent rather than less. Disabled = slate-100 fill,
> fg-subtle text, `cursor: not-allowed`.

### `input/`
40px, 1px border, radius-md, 12px horizontal padding.
States: default · hover (border-strong) · focus (brand ring) · disabled
(surface-subtle fill) · **error** (danger-600 border + danger-700 message).
Types used: `text`, `email`, `search`, `number`.

### `number-stepper/`
Input with `−` / `+` affordances, `min` / `max` / `step`. Used for
`contract_hours`, `min_hours`, `min_staff`, `max_staff`. Clamps on blur;
typing an out-of-range value shows the error state rather than silently
correcting.

### `select/`
Native `<select>` styled to match `input`, with a chevron. Native is deliberate
— keyboard behaviour and mobile pickers come free, and no option list here needs
custom rendering.

### `field/`
Wrapper: `label` (caption token) → control → `hint` (small, fg-muted) *or*
`error` (small, danger-700). Hint and error never show simultaneously — error
replaces hint. Wires `htmlFor`, `aria-describedby` and `aria-invalid`.

### `toggle-chip/`
The day/shift exclusion control. A real `<input type="checkbox">` visually
hidden, with a styled `<label>` — so keyboard, screen readers and form semantics
all work, while presenting as a compact pill.

Unselected: white fill, border, fg-muted. Selected: brand-100 fill, brand-200
border, brand-700 text, plus a check glyph — **selection is never conveyed by
fill alone**. Hover: surface-subtle. Focus: ring on the label.

Grouped in a `role="group"` with an accessible group label
("Days not available").

### `badge/`
Small status pill. Variants `neutral` · `success` · `warning` · `danger` ·
`info`, plus shift variants `morning` · `afternoon` · `evening` using the shift
tokens. Always text — never a bare coloured dot.

### `avatar/`
Initials on brand-50, radius-full, 32px (table) / 40px (drawer header). Derived
from `first_name[0] + last_name[0]`.

### `spinner/`
Rotating ring, `currentColor`, sizes 16 / 20 / 32. Honours reduced-motion by
slowing rather than stopping — a frozen spinner reads as a hang.

### `skeleton/`
Shimmering slate-100 block. Variants `text` · `circle` · `rect`. Skeletons
mirror the *shape* of what's coming — a table skeleton is rows of the right
height and column widths, not one grey slab.

---

## Composites

### `table/` (+ `table.css`)
Header row 40px, caption-token uppercase labels, sticky on scroll. Body rows
48px, zebra via surface-subtle, hover surface-subtle, 1px row separators.
Sortable headers show a direction chevron; the sorted column's header is
fg (not muted).
Right-most `Actions` column: ghost icon buttons, revealed on row hover but
**always present in the DOM and always reachable by keyboard**.
Slots for `empty` and `loading` states — see `04-patterns.md`.

> Fixed from the old UI: it used `<td>` inside `<thead>` instead of `<th>`, and
> its action icons were decorative SVGs with no button, no handler and no label.

### `search-input/`
Input with a leading magnifier icon and a clearing `×` once non-empty.
Debounced 250ms. Filters client-side over the loaded collection.

### `drawer/` (+ `drawer.css`)
Right-hand panel, 480px wide, full height, shadow-md, over a 30%-opacity slate
backdrop. Header (title + close), scrollable body, sticky footer with actions.
Slides in over `--duration-slow`.
Focus is trapped inside; `Esc` closes; focus returns to the trigger on close.
If the form is dirty, `Esc` and backdrop click ask for confirmation instead of
discarding silently.
Used for all create/edit forms.

### `modal/` and `confirm-dialog/`
Centred, max 480px, radius-lg, shadow-md. `confirm-dialog` is the destructive
specialisation: it **names the subject** ("Delete Kolade Adeyemi?"), states the
consequence, and its confirm button is `danger`. Default focus lands on Cancel.

### `toast/`
Bottom-right stack, max 3, auto-dismiss 5s (errors persist until dismissed).
Variants success · error · info. `role="status"`, `aria-live="polite"`.
Errors carry the server's message, never a generic string.

### `empty-state/`
Centred icon, one-line heading, one-line explanation, and the primary action
that resolves it. "No staff yet" always ships with an *Add staff* button.

### `week-picker/`
`‹` · `This week` · `›` with the range between them — *17 – 23 Aug 2026*.
Weeks run Monday→Sunday to match `DAY_OF_WEEK` in `app.py`. `This week` is
disabled when already on the current week. Keyboard: `←` / `→` when focused.

### `tabs/`
Underline style, brand-600 indicator on the active tab. Roving tabindex,
`role="tablist"`.

---

## Rota components

### `schedule-grid/` (+ `.css` in `pages/schedule/`)
Columns: `Mon…Sun`. Rows: grouped by department, three shift rows inside each.
Sticky header row (`--z-sticky`) and sticky first column so the
department/shift labels stay visible while scrolling a wide week.
Department group boundaries get a heavier top border than shift-row separators —
grouping is expressed by *border weight*, not by extra colour.

### `schedule-cell/`
One `(department, shift, day)`. Contains staff pills, a headcount `2/3`, and the
coverage treatment from `01-foundations.md`. Empty renders `—`, not blank.
Whole cell is a button: click opens the staff picker. Hover reveals a `+`.
Below `min_staff` → rose tint **and** a ⚠ with a tooltip naming the
shortfall.

### `staff-pill/`
Staff name in a rounded chip. Hover reveals `×` to unassign. A conflict
(exclusion violation, double-booking, over contract hours) shows a danger
border and an icon with an explanatory tooltip.

### `shift-legend/`
Maps the three shift colours to their names. Printed as well as shown — its
whole purpose is to make the grid decodable by someone holding the paper.

---

## Layout

### `layout/` (+ `layout.css`)
`AppShell` — flex: 260px sidebar, then a column of 64px topbar + scrollable
content (24px padding). Replaces the old `grid-cols-20 grid-rows-10` subgrid
shell, which tied every page's internals to a fixed 20×10 grid and broke as soon
as content didn't fit.

### `sidebar/`
Brand wordmark → nav (Schedule, Staff, Departments) → footer.
Active route: brand-50 fill, brand-700 text, and a 2px brand-600 left bar.
Nav items are `<NavLink>`s; the whole row is the hit target.

> Fixed from the old UI: `<Link to={null}>` on the Support/Sign Out items, and a
> `MenuItem` that compared against `'Scheduler'` while every caller passed
> `'Schedules'` — so the branch never fired.

### `navbar/` (topbar)
Left: page title. Right: page-level actions. On the schedule page it also holds
the week picker, Generate/Regenerate and Download PDF.

---
*Changelog: 2026-08-21 — initial.*
