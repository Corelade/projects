/**
 * Mock request handlers, keyed by the `mock` value each endpoint declares in
 * its `extraOptions`. Keying on that rather than on the URL means editing
 * endpoints.ts never breaks the mocks.
 */

import type {
  Department,
  DepartmentInput,
  ScheduleWeek,
  Staff,
  StaffInput,
  UpdateCellRequest,
} from '@/types'
import { weekEnd } from '@/lib/dates'
import * as db from './db'

const LATENCY_MS = 300

const delay = () => new Promise((r) => setTimeout(r, LATENCY_MS))

export interface MockResult {
  data?: unknown
  error?: { status: number; data: { detail: string } }
}

const fail = (status: number, detail: string): MockResult => ({
  error: { status, data: { detail } },
})

export type MockKey =
  | 'staff.list'
  | 'staff.create'
  | 'staff.update'
  | 'staff.remove'
  | 'departments.list'
  | 'departments.create'
  | 'departments.update'
  | 'departments.remove'
  | 'schedule.week'
  | 'schedule.generate'
  | 'schedule.updateCell'

/**
 * RTK Query freezes whatever it caches. Handing out references to the fixture
 * objects therefore freezes the fixture DB itself, and the next mutation throws
 * "Cannot assign to read only property". Every response is a deep copy.
 */
export async function handleMock(
  key: MockKey,
  body: unknown,
): Promise<MockResult> {
  const result = await route(key, body)
  return result.error ? result : { data: structuredClone(result.data) }
}

async function route(key: MockKey, body: unknown): Promise<MockResult> {
  await delay()

  switch (key) {
    // --- staff -----------------------------------------------------------
    case 'staff.list':
      return { data: [...db.staff] }

    case 'staff.create': {
      const input = body as StaffInput
      if (db.staff.some((s) => s.email === input.email)) {
        return fail(400, 'Email already exists')
      }
      const created: Staff = { ...input, id: db.nextStaffId() }
      db.staff.push(created)
      return { data: created }
    }

    case 'staff.update': {
      const input = body as Staff
      const i = db.staff.findIndex((s) => s.id === input.id)
      if (i === -1) return fail(404, 'Staff member not found')
      if (db.staff.some((s) => s.email === input.email && s.id !== input.id)) {
        return fail(400, 'Email already exists')
      }
      db.staff[i] = { ...input }
      return { data: db.staff[i] }
    }

    case 'staff.remove': {
      const { id } = body as { id: number }
      const i = db.staff.findIndex((s) => s.id === id)
      if (i === -1) return fail(404, 'Staff member not found')
      db.staff.splice(i, 1)
      // Drop them from every stored rota.
      for (const week of db.weeks.values()) {
        for (const cell of week.cells) {
          cell.staff = cell.staff.filter((a) => a.staff_id !== id)
        }
      }
      return { data: { id } }
    }

    // --- departments -----------------------------------------------------
    case 'departments.list':
      return { data: [...db.departments] }

    case 'departments.create': {
      const input = body as DepartmentInput
      const name = input.name.trim()
      if (
        db.departments.some(
          (d) => d.name.toLowerCase() === name.toLowerCase(),
        )
      ) {
        return fail(400, 'Department already exists')
      }
      const created: Department = {
        ...input,
        name: name,
        id: db.nextDeptId(),
      }
      db.departments.push(created)
      return { data: created }
    }

    case 'departments.update': {
      const input = body as Department
      const i = db.departments.findIndex((d) => d.id === input.id)
      if (i === -1) return fail(404, 'Department not found')
      db.departments[i] = { ...input }
      return { data: db.departments[i] }
    }

    case 'departments.remove': {
      const { id } = body as { id: number }
      const i = db.departments.findIndex((d) => d.id === id)
      if (i === -1) return fail(404, 'Department not found')
      db.departments.splice(i, 1)
      for (const week of db.weeks.values()) {
        week.cells = week.cells.filter((c) => c.department_id !== id)
      }
      return { data: { id } }
    }

    // --- schedule --------------------------------------------------------
    case 'schedule.week': {
      const { week_start } = body as { week_start: string }
      const existing = db.weeks.get(week_start)
      if (existing) return { data: existing }
      // No rota yet for this week — the empty state.
      const empty: ScheduleWeek = {
        week_start,
        week_end: weekEnd(week_start),
        generated_at: null,
        cells: [],
      }
      return { data: empty }
    }

    case 'schedule.generate': {
      const { week_start } = body as { week_start: string }
      if (!db.staff.length || !db.departments.length) {
        return fail(
          422,
          'Add at least one department and one staff member before generating a rota.',
        )
      }
      const built = db.buildWeek(week_start)
      db.weeks.set(week_start, built)
      return { data: built }
    }

    case 'schedule.updateCell': {
      const patch = body as UpdateCellRequest
      const week = db.weeks.get(patch.week_start)
      if (!week) return fail(404, 'No rota for that week')

      const cell = week.cells.find(
        (c) =>
          c.department_id === patch.department_id &&
          c.day === patch.day &&
          c.shift === patch.shift,
      )
      if (!cell) return fail(404, 'Cell not found')

      cell.staff = patch.staff_ids
        .map((id) => db.staff.find((s) => s.id === id))
        .filter((s): s is Staff => Boolean(s))
        .map((s) => ({
          staff_id: s.id,
          staff_name: `${s.first_name} ${s.last_name}`,
        }))

      return { data: cell }
    }

    default:
      return fail(500, `No mock handler for "${key}"`)
  }
}
