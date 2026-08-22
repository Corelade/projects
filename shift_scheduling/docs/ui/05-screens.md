# 05 — Screens

Three screens. Each is `pages/<name>/<name>.tsx` with an optional
`<name>.css` beside it.

Routes:

| Path | Screen |
|---|---|
| `/` | redirect → `/schedule` |
| `/schedule` | Rota |
| `/staff` | Staff list |
| `/staff/new` | Staff list + create drawer |
| `/staff/:id/edit` | Staff list + edit drawer |
| `/departments` | Departments list |
| `/departments/new` | + create drawer |
| `/departments/:id/edit` | + edit drawer |

Drawer routes are nested children of the list route, so the list stays mounted
behind the drawer and Back closes it.

---

## Shell

```
┌───────────┬────────────────────────────────────────────────────────┐
│ ShiftPro  │  Page title            [ page actions ]                │ 64px
│           ├────────────────────────────────────────────────────────┤
│ ▸ Schedule│                                                        │
│   Staff   │                    content (scrolls)                   │
│   Depts   │                                                        │
│           │                                                        │
│           │                                                        │
│  Support  │                                                        │
│  Sign out │                                                        │
└───────────┴────────────────────────────────────────────────────────┘
   260px
```

Sidebar and topbar are `display: none` in print.

---

## `/schedule` — the rota

```
 Rota          ‹  17 – 23 Aug 2026  ›   [This week]  [Generate]  [⤓ PDF]
─────────────────────────────────────────────────────────────────────────
 ● Morning   ● Afternoon   ● Evening          ⚠ below minimum staffing
─────────────────────────────────────────────────────────────────────────
              │ Mon 17 │ Tue 18 │ Wed 19 │ Thu 20 │ Fri 21 │ Sat │ Sun
━━━━━━━━━━━━━━┿━━━━━━━━┿━━━━━━━━┿━━━━━━━━┿━━━━━━━━┿━━━━━━━━┿━━━━━┿━━━━━
 SHOES        │        │        │        │        │        │     │
   Morning 1/1│ Kolade │ Riri   │ Loli   │ Kola   │ Shem   │ …   │ …
   Afternoon  │ Shem   │ Kola   │ Shem   │ Riri   │ Loli   │     │
     2/3      │ Loli   │        │        │        │        │     │
   Evening 1/3│ Dara   │ Kunle  │ Kola   │ Dara   │ Kunle  │     │
━━━━━━━━━━━━━━┿━━━━━━━━┿━━━━━━━━┿━━━━━━━━┿━━━━━━━━┿━━━━━━━━┿━━━━━┿━━━━━
 CASHIER      │        │        │        │        │        │     │
   Morning 1/1│ Core   │ Lanre  │ Core   │ Lanre  │ Core   │     │
   Afternoon  │ Riri   │ Tayo   │ Lanre  │ Tayo   │ Riri   │     │
     2/3      │ Lanre  │        │        │        │        │     │
 ⚠ Evening 0/2│   —    │ Core   │ Riri   │ Core   │ Kunle  │     │
━━━━━━━━━━━━━━┷━━━━━━━━┷━━━━━━━━┷━━━━━━━━┷━━━━━━━━┷━━━━━━━━┷━━━━━┷━━━━━
```

**Regions**

1. **Topbar** — title, `week-picker`, `Generate` / `Regenerate`, `Download PDF`.
2. **Legend** — shift colours + the ⚠ meaning. Prints.
3. **Grid** — sticky header row, sticky first column. Department groups
   separated by a heavier rule than the shift rows within them.

**Behaviours**

| Action | Result |
|---|---|
| `‹` / `›` | Loads that week. URL carries `?week=2026-08-17` so a week is linkable. |
| `Generate` | Runs the solver for the shown week. If a rota already exists, confirms first (`04-patterns.md`). Button goes `loading`; the existing grid stays visible. |
| Generation fails | Inline error panel above the grid carrying the reason — which department, which constraint. Never a bare "failed". |
| Click a cell | Opens the staff picker: searchable list, staff already unavailable that day/shift shown disabled with the reason. |
| Click `×` on a pill | Unassigns, optimistically. |
| Hover a ⚠ | Tooltip: "Cashier needs at least 2 staff on Monday evening." |

**States** — loading: grid skeleton with real column widths. Empty (no rota for
this week): `empty-state` with a *Generate rota* button. Error: inline panel +
Retry.

The whole `nondeterministic solver` fact is user-visible: regenerating the same
week yields a different valid rota. The confirm copy says so — "The current
assignments for this week will be replaced."

---

## `/staff`

```
 Staff                                              [ + Add staff ]
─────────────────────────────────────────────────────────────────────
 [ 🔍 Search staff              ]
─────────────────────────────────────────────────────────────────────
 NAME              POSITION    CONTRACT  MIN   UNAVAILABLE      
─────────────────────────────────────────────────────────────────────
 (KA) Kolade A.    Associate     40 h    8 h   Wed, Sat · PM   ✎ 🗑
 (RO) Riri O.      Management    32 h   16 h   —               ✎ 🗑
 (CS) Core S.      Associate     24 h    8 h   Sun             ✎ 🗑
─────────────────────────────────────────────────────────────────────
 Showing 3 of 3 staff
```

The **Unavailable** column summarises both exclusion lists compactly —
`Wed, Sat · PM`. Full detail lives in the edit drawer.

### Staff drawer

```
 Add staff                                                    ✕
─────────────────────────────────────────────────────────────────
 First name            Last name
 [                 ]   [                 ]

 Email
 [                                       ]

 Position                Contract hours    Min hours
 [ Associate      ▾ ]    [ − 40 + ]        [ − 8 + ]

 DAYS NOT AVAILABLE
 (Mon)(Tue)(Wed)(Thu)(Fri)(Sat)(Sun)

 SHIFTS NOT AVAILABLE
 (Morning)(Afternoon)(Evening)

 ⓘ 40 of 84 possible hours available.
─────────────────────────────────────────────────────────────────
                                    [ Cancel ]  [ Add staff ]
```

`position` defaults to **Associate**. The live availability hint recomputes
`(12 − 4×shifts) × (7 − days)` as chips toggle and turns into an error the
moment it drops below `contract_hours` — so an infeasible person can't be saved.

---

## `/departments`

```
 Departments                                    [ + Add department ]
─────────────────────────────────────────────────────────────────────
 [ 🔍 Search departments        ]
─────────────────────────────────────────────────────────────────────
 DEPARTMENT       MIN STAFF   MAX STAFF   
─────────────────────────────────────────────────────────────────────
 Shoes                1           3       ✎ 🗑
 Cashier              2           3       ✎ 🗑
 Home                 1           2       ✎ 🗑
─────────────────────────────────────────────────────────────────────
 Showing 3 of 3 departments
```

### Department drawer

```
 Add department                                                ✕
─────────────────────────────────────────────────────────────────
 Department name
 [                                       ]

 Min staff          Max staff
 [ − 1 + ]          [ − 3 + ]

 ⓘ Needs 21 staff-shifts per week.
─────────────────────────────────────────────────────────────────
                                    [ Cancel ]  [ Add department ]
```

Delete confirmation warns that the department's assignments disappear from
existing rotas.

---

## Responsive

Desktop-first. Below 1280px the sidebar collapses to icons; below 1024px it
becomes a slide-over. The rota grid never reflows — it scrolls horizontally with
its sticky first column, because a week is a week.

---
*Changelog: 2026-08-21 — initial.*
