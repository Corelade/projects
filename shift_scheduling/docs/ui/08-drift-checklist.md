# 08 — Drift Checklist

Run this at the end of every phase and before any merge. Each item is either
mechanical (a command) or a specific thing to look at — nothing here is "does it
look right?".

Record the date and outcome at the bottom.

---

## 1. Tokens — mechanical

```bash
cd web

# No literal hex outside theme.css
grep -rnE '#[0-9a-fA-F]{3,8}\b' src --include='*.tsx' --include='*.ts' --include='*.css' \
  | grep -v 'styles/theme.css'

# No arbitrary Tailwind values
grep -rnE 'class(Name)?="[^"]*\[[0-9]' src --include='*.tsx'

# No raw rgb()/hsl() outside theme.css
grep -rnE '\b(rgb|hsl)a?\(' src --include='*.tsx' --include='*.css' \
  | grep -v 'styles/theme.css'

# No outline suppression without a replacement
grep -rn 'outline: *none\|outline-none' src
```

All four must return nothing, with one sanctioned exception: the numeric input
inside `number-stepper` sets `outline-none` because its **wrapper** carries the
focus ring (`has-[:focus-visible]:outline-*`). That is a replacement, not a
suppression. Any other hit is drift: either use a token, or add one to
`02-tokens.md` **and** `theme.css` in the same commit.

- [ ] Every token in `02-tokens.md` exists in `theme.css`
- [ ] Every token in `theme.css` exists in `02-tokens.md`
- [ ] Components use semantic aliases (`text-fg`) over ramp steps (`text-slate-900`)

## 2. Structure

- [ ] Every component is `components/<name>/<name>.tsx`
- [ ] Every page is `pages/<name>/<name>.tsx`
- [ ] `.css` files sit beside their component/page, named to match
- [ ] No `.css` file contains a literal colour, px size, radius or shadow
- [ ] No component reaches into another component's folder for styles

## 3. Components

For each entry in `03-components.md`:

- [ ] It exists at the documented path
- [ ] Every documented variant is implemented
- [ ] `default` / `hover` / `focus-visible` / `active` / `disabled` all present
- [ ] `loading` and `error` present where applicable
- [ ] Button width doesn't change when it enters `loading`
- [ ] Disabled styling reads as *less* prominent than enabled
- [ ] Every icon-only control has an `aria-label`

## 4. Patterns

- [ ] Every data view implements loading, empty, error and loaded
- [ ] Loading is a shaped skeleton, not a lone spinner
- [ ] A failed load renders an error panel with Retry — never "no items yet"
- [ ] Forms validate on blur, re-validate on change only once errored
- [ ] Failed submit preserves input and maps field errors to fields
- [ ] Dirty forms confirm before discarding
- [ ] Every destructive action confirms, naming its subject
- [ ] Table footer counts are computed, never hard-coded
- [ ] Error copy carries the server's message, not a generic string

## 5. Rota

- [ ] One cell = one `(department, shift, day)`
- [ ] Header row and first column stay sticky while scrolling
- [ ] Department groups are separated by border weight, not extra colour
- [ ] Cells below `min_staff` show ⚠ **and** the headcount, not just a tint
- [ ] Empty cells render `—`
- [ ] Every shift cell names its shift — colour is never the only signal
- [ ] Legend is present on screen and in print
- [ ] Week navigation updates `?week=` and is linkable
- [ ] Regenerating an existing week confirms first
- [ ] A failed generate shows the reason, not "failed"

## 6. Print & PDF

- [ ] ⌘P → A4 landscape, header repeats, no department split across pages
- [ ] Printed in greyscale, every shift and warning is still identifiable
- [ ] Legend prints
- [ ] Sidebar, topbar and all controls are hidden in print
- [ ] PDF text is selectable in a viewer (vector, not a screenshot)
- [ ] PDF matches the screen: same staff, order and warnings
- [ ] 8+ departments paginate cleanly
- [ ] Download button is disabled when there is no rota

## 7. State

- [ ] Every API URL lives in `store/api/endpoints.ts`:

      ```bash
      grep -rnE "\\bfetch\\(|https?://|VITE_API_BASE_URL" src/components src/pages \\
        | grep -v 'w3.org'
      ```

      Three traps this check has already fallen into: `fetch\\(` without `\\b`
      also matches RTK Query's `refetch()`; matching bare paths like `'/staff'`
      flags react-router *routes*, which legitimately live in components; and
      `https?://` matches the SVG `xmlns` namespace, which is an identifier,
      not a request. Match transport, not paths.
- [ ] No server data is copied into `ui-slice`
- [ ] Tag invalidation matches the table in `07-state.md`
- [ ] Cell edits are optimistic and roll back on failure
- [ ] Drawer state derives from the route, not the slice
- [ ] `VITE_USE_MOCKS=true` exercises loading, empty, error and understaffed cases

## 8. Accessibility

- [ ] Text contrast ≥ 4.5:1, borders ≥ 3:1
- [ ] Visible focus ring on every interactive element
- [ ] Drawer/modal trap focus, close on `Esc`, restore focus
- [ ] Rota is a real `<table>` with `<th scope>`
- [ ] Toggle chips are real checkboxes underneath, with a group label
- [ ] `prefers-reduced-motion` honoured
- [ ] Keyboard-only pass: create, edit and delete a staff member without a mouse

## 9. Build

```bash
npm run build   # tsc -b + vite, zero errors
npm run lint    # zero warnings
```

- [ ] No `any` in `types/`
- [ ] No `console.log` left in `src/`
- [ ] No `// @ts-ignore`

---

## When something fails

Two legitimate outcomes, never a third:

1. **Code is wrong** → fix the code.
2. **Doc is wrong** → change the doc in its own commit, note it in that file's
   changelog, and say why.

Leaving a known deviation unrecorded is what this document exists to prevent.

---

## Audit log

| Date | Phase | Result | Notes |
|---|---|---|---|
| 2026-08-21 | 9 | 4 findings, all fixed | 1. Literal hex/`rgb()` in `print.css`, `drawer.css`, `globals.css` → tokenised. 2. `number-stepper`'s inner input suppressed focus with no replacement → wrapper now carries the ring. 3. `schedule.tsx` used `window.location.href` for an in-app link → full page reload, changed to `navigate()`. 4. Eight tokens existed in `theme.css` but not in `02-tokens.md` → documented. The URL grep itself was wrong and was rewritten. |
