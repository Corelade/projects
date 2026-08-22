# 04 — Patterns

How primitives combine. These are the rules that keep three screens built at
different times feeling like one product.

---

## The four states of every data view

Every screen that loads data implements all four. A screen with only the happy
path is incomplete.

| State | Treatment |
|---|---|
| **Loading** | Skeleton shaped like the eventual content — table skeletons are rows at 48px with the real column widths. Never a lone centred spinner on a blank page. |
| **Empty** | `empty-state`: icon, "No staff yet", one line of explanation, and the button that fixes it. |
| **Error** | Inline panel inside the content area — icon, the server's actual message, a **Retry** button. Never a toast alone; a toast disappears and leaves an empty screen behind. |
| **Loaded** | The content. |

**Empty ≠ error ≠ loading.** A failed request must never render as "No staff yet" —
that tells the user their data is gone.

---

## Forms

Live in a `drawer`, opened from a route (`/staff/new`, `/staff/:id/edit`) so the
URL is shareable and Back closes the form.

**Layout** — single column, 16px between fields, 24px between sections. Related
short fields pair horizontally (`contract_hours` + `min_hours`). Labels above
inputs, always.

**Validation timing**
- On blur for the field just left.
- On change, but *only* for a field already showing an error — so errors clear
  as they're fixed rather than nagging while typing.
- On submit for everything.

**Submitting** — the submit button enters `loading`, all inputs disable, the
drawer stays open. On success: close, toast, list refetches. On failure: stay
open, map field errors to their fields, show non-field errors in a panel at the
top of the form. **Never clear the user's input on failure.**

> Fixed from the old UI: it disabled submit via a blanket "is any field empty"
> check with no message, so the button was dead and the form never said why.
> Here submit stays enabled and pressing it reveals what's wrong.

**Dirty guard** — a modified form confirms before discarding on `Esc`, backdrop
click, or navigation.

### Client-side validation rules

Mirrors the domain rules so feedback is instant. The server remains the
authority; these only pre-empt round trips.

| Rule | Message | Source |
|---|---|---|
| `contract_hours` 8–40 | "Contract hours must be between 8 and 40." | `classes.py:80-94` |
| `8 ≤ min_hours ≤ contract_hours` | "Minimum hours can't exceed contract hours." | `classes.py:70-78` |
| `(12 − 4×excluded_shifts) × (7 − excluded_days) ≥ contract_hours` | "These exclusions leave only N hours available — not enough for a M-hour contract." | `classes.py:96-113` |
| `min_staff ≤ max_staff` | "Minimum staff can't exceed maximum staff." | `classes.py:138-206` |
| `email` unique | Surfaced from the server's 400 onto the email field | `api.py` |

The exclusion rule is the valuable one: it catches an impossible staff member at
entry time instead of letting the whole solve fail later with no obvious cause.

---

## Tables

Columns are chosen so the first is identity and the last is actions.

| Rule | Detail |
|---|---|
| Sort | Click a header. Default sort: name ascending. |
| Search | `search-input` above the table, debounced, client-side. |
| Row actions | Ghost icon buttons: edit (pencil), delete (trash). Revealed on hover, always in the DOM, always keyboard-reachable. |
| Row click | Opens edit — same as the pencil. |
| Footer | "Showing 12 of 12 staff". The count reflects filtering, and is never hard-coded. |
| Numbers | `tabular-nums`, right-aligned. |

> Fixed from the old UI: its footer read "Showing N of 24" with 24 as a literal,
> and the action icons were inert SVGs.

---

## Destructive actions

Always `confirm-dialog`, never an immediate delete, never an undo-toast alone.

The dialog **names the subject** and states the consequence:

> **Delete Kolade Adeyemi?**
> They'll be removed from all future rotas. This can't be undone.
> [Cancel] [Delete]

Cancel takes default focus. Confirm is `danger`. While deleting, confirm goes
`loading` and both buttons disable.

Regenerating an existing rota is destructive too and gets the same treatment:

> **Regenerate the rota for 17 – 23 Aug?**
> The current assignments for this week will be replaced.

---

## Feedback

| Event | Feedback |
|---|---|
| Create / update / delete succeeds | Success toast, 5s |
| Create / update / delete fails | Error toast **and** inline field errors; toast persists |
| Load fails | Inline error panel with Retry — not a toast |
| Long operation (generate) | Button `loading` + progress copy; the grid keeps showing the previous week's data rather than blanking |

Copy is specific. "Staff created" not "Success". "Cashier needs at least 2 staff
on Tuesday evening" not "Invalid schedule".

---

## Optimistic updates

Rota cell edits apply immediately via RTK Query's `onQueryStarted` +
`updateQueryData`, and roll back on failure with an error toast. Assigning
someone should feel like moving a magnet on a whiteboard.

Staff and department mutations are **not** optimistic — they're infrequent, and
invalidating the tag is simpler and less surprising.

---

## Accessibility floor

Non-negotiable, checked in the drift audit:

- Text contrast ≥ 4.5:1; UI borders ≥ 3:1.
- Visible `:focus-visible` ring on everything interactive.
- Every icon-only control has an `aria-label`.
- Drawers and modals trap focus, close on `Esc`, restore focus on close.
- Colour is never the sole carrier of meaning — shift, coverage and chip
  selection each pair colour with text or an icon.
- The rota grid is a real `<table>` with `<th scope>`, so it is navigable and
  announced correctly.
- `prefers-reduced-motion` honoured.

---

## Copy

Sentence case for everything except `caption`-token labels, which are uppercase.
Buttons are verbs — *Add staff*, *Save changes*, *Generate rota*. Never *OK* or
*Submit*.

Days and shifts display capitalised (Monday, Morning) but travel over the wire
lowercase, matching `DAY_OF_WEEK` and `shift_time` in `app.py:9-18`.

---
*Changelog: 2026-08-21 — initial.*
