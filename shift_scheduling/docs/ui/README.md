# ShiftPro UI — Design System

This folder is the **source of truth** for the ShiftPro interface. It is written
before the code and the code is audited against it.

If the code and these documents disagree, one of two things must happen — never
neither:

1. The code is wrong → fix the code.
2. The document is wrong → change the document deliberately, in its own commit,
   with a note in the changelog at the bottom of the affected file.

Silent divergence is the failure mode this folder exists to prevent.

---

## Reading order

| File | What it settles |
|---|---|
| `00-principles.md` | What the product is, who uses it, what we optimise for |
| `01-foundations.md` | Colour, type, space, radius, shadow, icon, motion |
| `02-tokens.md` | The canonical token table — maps 1:1 to `web/src/styles/theme.css` |
| `03-components.md` | Every primitive: anatomy, variants, states |
| `04-patterns.md` | How primitives combine — forms, tables, empty/loading/error, destructive actions |
| `05-screens.md` | Each screen's regions and behaviours |
| `06-print.md` | Print stylesheet and PDF export rules |
| `07-state.md` | Redux Toolkit / RTK Query structure and the endpoint map |
| `08-drift-checklist.md` | The audit |

---

## The one rule that makes drift mechanical

**No colour, font size, spacing value, radius or shadow is written literally
anywhere except `web/src/styles/theme.css`.**

Everything else consumes a token. That turns "has the UI drifted?" from a
subjective design review into a grep:

```bash
# Should return nothing outside theme.css
grep -rnE '#[0-9a-fA-F]{3,8}\b' web/src --include=*.tsx --include=*.ts
grep -rnE '\[[0-9]+px\]' web/src --include=*.tsx
```

See `08-drift-checklist.md` for the full audit.

---

## Scope

Covered: schedule (view, update, print), staff CRUD, departments CRUD.

Not covered in this pass: authentication, dark mode (tokens are structured to
allow it later), mobile-first layouts, dashboard, settings.
