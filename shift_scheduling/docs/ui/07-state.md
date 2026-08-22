# 07 — State

Redux Toolkit. **RTK Query owns all server data**; a single `uiSlice` owns
client-only state. Nothing that comes from the API is ever copied into a slice —
that duplication is how caches go stale.

```
store/
  index.ts                  configureStore
  api/
    endpoints.ts            ← every URL, in one place
    base-api.ts             createApi + fetchBaseQuery + tagTypes
    staff-api.ts            injectEndpoints
    departments-api.ts
    schedule-api.ts
  slices/
    ui-slice.ts             week, drawer, toasts, filters
types/
  staff.ts  department.ts  schedule.ts  common.ts
mocks/
  staff.ts  departments.ts  schedule.ts  index.ts
```

---

## `endpoints.ts` — the mapping surface

The backend routes don't exist yet. **This is the only file that needs editing
when they do.** Nothing else in the app writes a URL.

```ts
export const ENDPOINTS = {
  staff: {
    list:   '/list_staff',
    create: '/create-staff',
    update: (id: number) => `/staff/${id}`,
    remove: (id: number) => `/staff/${id}`,
  },
  departments: {
    list:   '/departments',
    create: '/create_department',
    update: (id: number) => `/departments/${id}`,
    remove: (id: number) => `/departments/${id}`,
  },
  schedule: {
    week:     (weekStart: string) => `/schedule?week_start=${weekStart}`,
    generate: '/schedule/generate',
    update:   '/schedule/update',
  },
} as const
```

`list` and `create` reflect the routes that exist in `api.py` today. The rest are
placeholders — rename them to whatever gets built.

If a response shape differs from what the UI expects, fix it in that endpoint's
`transformResponse` rather than reshaping components.

---

## Types

Mirrors the domain classes the solver consumes (`classes.py`), not the raw ORM
rows.

```ts
// types/common.ts
export type Day = 'monday' | 'tuesday' | 'wednesday' | 'thursday'
                | 'friday' | 'saturday' | 'sunday'
export type Shift = 'morning' | 'afternoon' | 'evening'
export type Position = 'associate' | 'management' | 'loss_protection'

// types/staff.ts
export interface Staff {
  id: number
  first_name: string
  last_name: string
  email: string
  position: Position          // defaults to 'associate'
  contract_hours: number      // 8–40
  min_hours: number           // 8 ≤ min_hours ≤ contract_hours
  day_exclusions: Day[]       // "days not available"
  shift_exclusions: Shift[]   // "shifts not available"
}
export type StaffInput = Omit<Staff, 'id'>

// types/department.ts
export interface Department {
  id: number
  name: string
  min_staff: number
  max_staff: number
}
export type DepartmentInput = Omit<Department, 'id'>

// types/schedule.ts
export interface Assignment {
  staff_id: number
  staff_name: string          // display; avoids a join on every cell
}
export interface ScheduleCell {
  department_id: number
  day: Day
  shift: Shift
  staff: Assignment[]
}
export interface ScheduleWeek {
  week_start: string          // ISO date, always a Monday
  week_end: string
  generated_at: string | null
  cells: ScheduleCell[]
}
```

**Note on the wire format.** `app.py`'s `to_normal_dict` collapses the solver's
result to bare name strings, dropping every ID. The UI needs IDs to edit a cell,
so `ScheduleCell` carries `department_id` and `staff_id`. Whatever the endpoint
returns gets normalised into this flat `cells` array in
`schedule-api.ts`'s `transformResponse` — a flat list is far easier to index,
diff and optimistically patch than the nested day→department→shift object.

---

## `base-api.ts`

```ts
tagTypes: ['Staff', 'Department', 'Schedule']
baseUrl: import.meta.env.VITE_API_BASE_URL
```

Tag strategy:

| Mutation | Invalidates |
|---|---|
| create/update/delete staff | `Staff`, and `Schedule` (rotas reference staff) |
| create/update/delete department | `Department`, `Schedule` |
| generate schedule | `Schedule` for that week |
| update schedule cell | nothing — patched optimistically |

---

## Optimistic cell updates

```ts
async onQueryStarted({ weekStart, ...patch }, { dispatch, queryFulfilled }) {
  const undo = dispatch(
    scheduleApi.util.updateQueryData('getWeek', weekStart, draft => {
      applyCellPatch(draft, patch)
    })
  )
  try { await queryFulfilled } catch { undo.undo() }
}
```

Assigning someone should feel immediate. Staff and department mutations are
**not** optimistic — they're rare, and tag invalidation is simpler and less
surprising.

---

## `ui-slice.ts`

Client-only. Never mirrors server data.

```ts
{
  selectedWeekStart: string      // ISO Monday; also synced to ?week=
  staffSearch: string
  departmentSearch: string
  staffSort: { key: keyof Staff; dir: 'asc' | 'desc' }
  toasts: Toast[]
}
```

Drawer open/closed is **not** here — it's derived from the route
(`/staff/new`, `/staff/:id/edit`), so Back closes the form and URLs stay
shareable.

---

## Mocks

`VITE_USE_MOCKS=true` swaps `fetchBaseQuery` for a fake base query that resolves
from `mocks/` after a short delay. This makes the entire UI — generate, edit,
print, PDF, plus loading, empty and error states — reviewable **before any
endpoint exists**.

The fixtures deliberately include the awkward cases:
- a department below `min_staff` on one shift, so the ⚠ path renders
- a staff member with heavy exclusions, so the availability warning renders
- an empty week, so the empty state renders
- a week that returns a 500, so the error path renders

Setting `VITE_USE_MOCKS=false` is the only change needed to go live, aside from
the URLs in `endpoints.ts`.

---
*Changelog: 2026-08-21 — initial.*
