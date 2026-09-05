# 00 — Principles

## The product

ShiftPro builds a **weekly rota** for a retail operation split into
**departments**. Each day has three shifts — morning, afternoon, evening — of
four hours each. A constraint solver assigns staff to
`(day × department × shift)` cells subject to department min/max headcount,
per-staff contract hours, and per-staff day/shift exclusions.

The UI's job is to let a manager configure the inputs, run the solver, correct
its output by hand, and get the result onto paper.

## Who uses it

A **shift manager** at a desktop, typically once a week. They are not a
technical user. They care about three questions, in this order:

1. Is anyone unassigned who should be working?
2. Is any department short-staffed?
3. Can I print this and pin it up?

Everything else is secondary.

## Principles

**1. The rota is the product.**
The schedule grid is the screen people spend their time on. Staff and department
management exist to feed it. Design effort is allocated accordingly — the grid
gets the density, the affordances and the polish; CRUD screens get consistency
and speed.

**2. Dense, not cramped.**
A full week is 7 days × N departments × 3 shifts. That has to fit on one screen
and one sheet of paper. We use a 14px body size, 48px rows and tight but
consistent padding. Density is achieved by removing decoration, never by
removing whitespace between logical groups.

**3. Print is a first-class output, not an afterthought.**
Rotas get printed and pinned to walls. Every visual decision in the grid is
tested in greyscale on landscape A4. If it only works on screen, it doesn't
work.

**4. Never encode meaning in colour alone.**
Shift identity and coverage warnings always carry a text label or icon in
addition to their colour. This is required by print (mono) and by colour-vision
accessibility. It is not a nice-to-have — a rota that is ambiguous when
photocopied has failed.

**5. Every state is designed.**
Loading, empty, error and partial states are specified in `04-patterns.md`
alongside the happy path. A screen is not complete until all four are built.
Loading is a skeleton with the shape of the eventual content, never a bare
spinner in the middle of a blank page.

**6. Destructive actions are always confirmed, never undone by surprise.**
Deleting staff or a department, and regenerating a rota that already exists,
each require explicit confirmation naming the thing being affected.

**7. Tell the user why, not just that.**
The solver can fail to find a feasible schedule. "Generation failed" is not
acceptable copy. The UI surfaces the reason — which constraint, which
department, which staff member.

**8. One source of truth for tokens.**
`02-tokens.md` → `theme.css`. Nothing else defines a colour or a size. This is
what makes the anti-drift audit possible.

## Non-goals

- Real-time collaboration or multi-user presence.
- Mobile-first. Still desktop-first — the layouts are designed at full width and
  adapted downwards, and the rota grid assumes a wide viewport and scrolls
  rather than reflowing. It does now work on a phone; see `05-screens.md`.
- Theming beyond the single light palette. Dark mode is enabled by the token
  structure but not built.

---
*Changelog:*
*2026-08-21 — initial.*
*2026-09-05 — the mobile non-goal was narrowed: phone layouts are built, but
the design is still authored desktop-first.*
