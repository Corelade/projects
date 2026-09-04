/**
 * In-memory fixture database, used when VITE_USE_MOCKS=true.
 *
 * The fixtures deliberately include the awkward cases so every documented
 * state is reachable without a backend (docs/ui/07-state.md):
 *   - Cashier evening is below min_staff  -> the understaffed path
 *   - Loli has heavy exclusions               -> the availability warning
 *   - Weeks other than the seeded one are empty -> the empty state
 */

import type {
  Department,
  ScheduleCell,
  ScheduleWeek,
  Staff,
} from '@/types'
import { DAYS, SHIFTS } from '@/types'
import { currentWeekStart, weekEnd } from '@/lib/dates'

let staffSeq = 0
let deptSeq = 0

export const staff: Staff[] = [
  {
    id: ++staffSeq,
    first_name: 'Kolade',
    last_name: 'Adeyemi',
    email: 'kolade@shiftpro.test',
    position: 'associate',
    contract_hours: 40,
    min_hours: 8,
    day_exclusions: ['wednesday', 'saturday'],
    shift_exclusions: ['afternoon'],
  },
  {
    id: ++staffSeq,
    first_name: 'Riri',
    last_name: 'Okafor',
    email: 'riri@shiftpro.test',
    position: 'management',
    contract_hours: 32,
    min_hours: 16,
    day_exclusions: [],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Core',
    last_name: 'Salami',
    email: 'core@shiftpro.test',
    position: 'associate',
    contract_hours: 24,
    min_hours: 8,
    day_exclusions: ['sunday'],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Shem',
    last_name: 'Bello',
    email: 'shem@shiftpro.test',
    position: 'associate',
    contract_hours: 36,
    min_hours: 12,
    day_exclusions: ['monday'],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Loli',
    last_name: 'Nwosu',
    email: 'loli@shiftpro.test',
    position: 'associate',
    // Heavy exclusions: 2 shifts and 3 days blocked leaves 16 hours.
    contract_hours: 16,
    min_hours: 8,
    day_exclusions: ['friday', 'saturday', 'sunday'],
    shift_exclusions: ['morning', 'evening'],
  },
  {
    id: ++staffSeq,
    first_name: 'Dara',
    last_name: 'Ibrahim',
    email: 'dara@shiftpro.test',
    position: 'loss_protection',
    contract_hours: 40,
    min_hours: 20,
    day_exclusions: [],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Kunle',
    last_name: 'Ojo',
    email: 'kunle@shiftpro.test',
    position: 'associate',
    contract_hours: 28,
    min_hours: 8,
    day_exclusions: ['tuesday'],
    shift_exclusions: ['morning'],
  },
  {
    id: ++staffSeq,
    first_name: 'Lanre',
    last_name: 'Balogun',
    email: 'lanre@shiftpro.test',
    position: 'associate',
    contract_hours: 32,
    min_hours: 12,
    day_exclusions: [],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Motun',
    last_name: 'Eze',
    email: 'motun@shiftpro.test',
    position: 'management',
    contract_hours: 40,
    min_hours: 16,
    day_exclusions: ['saturday'],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Tayo',
    last_name: 'Aliyu',
    email: 'tayo@shiftpro.test',
    position: 'associate',
    contract_hours: 24,
    min_hours: 8,
    day_exclusions: ['thursday'],
    shift_exclusions: ['evening'],
  },
  {
    id: ++staffSeq,
    first_name: 'Amaka',
    last_name: 'Chukwu',
    email: 'amaka@shiftpro.test',
    position: 'associate',
    contract_hours: 40,
    min_hours: 16,
    day_exclusions: [],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Bisi',
    last_name: 'Adeleke',
    email: 'bisi@shiftpro.test',
    position: 'associate',
    contract_hours: 36,
    min_hours: 12,
    day_exclusions: ['wednesday'],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Chidi',
    last_name: 'Umeh',
    email: 'chidi@shiftpro.test',
    position: 'loss_protection',
    contract_hours: 40,
    min_hours: 20,
    day_exclusions: [],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Femi',
    last_name: 'Ogunleye',
    email: 'femi@shiftpro.test',
    position: 'associate',
    contract_hours: 32,
    min_hours: 8,
    day_exclusions: ['friday'],
    shift_exclusions: ['morning'],
  },
  {
    id: ++staffSeq,
    first_name: 'Grace',
    last_name: 'Nnaji',
    email: 'grace@shiftpro.test',
    position: 'management',
    contract_hours: 40,
    min_hours: 20,
    day_exclusions: [],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Hassan',
    last_name: 'Yusuf',
    email: 'hassan@shiftpro.test',
    position: 'associate',
    contract_hours: 36,
    min_hours: 12,
    day_exclusions: ['sunday'],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Ifeoma',
    last_name: 'Obi',
    email: 'ifeoma@shiftpro.test',
    position: 'associate',
    contract_hours: 40,
    min_hours: 16,
    day_exclusions: [],
    shift_exclusions: [],
  },
  {
    id: ++staffSeq,
    first_name: 'Jide',
    last_name: 'Fawole',
    email: 'jide@shiftpro.test',
    position: 'associate',
    contract_hours: 36,
    min_hours: 12,
    day_exclusions: ['tuesday'],
    shift_exclusions: ['evening'],
  },
]

export const departments: Department[] = [
  { id: ++deptSeq, name: 'Shoes', min_staff: 1, max_staff: 3 },
  { id: ++deptSeq, name: 'Cashier', min_staff: 2, max_staff: 3 },
  { id: ++deptSeq, name: 'Home', min_staff: 1, max_staff: 2 },
]

/** week_start -> week */
export const weeks = new Map<string, ScheduleWeek>()

/** Accounts for the mock auth handlers. Passwords in plain text on purpose —
 *  these are fixtures, and nothing here ever leaves the browser. */
export const users: { id: number; username: string; password: string }[] = [
  { id: 1, username: 'kolade', password: 'shiftpro123' },
]

let userSeq = 1
export const nextUserId = () => ++userSeq

export const nextStaffId = () => ++staffSeq
export const nextDeptId = () => ++deptSeq

// ---------------------------------------------------------------------------
// A deliberately simple stand-in for the real backtracking solver. It respects
// exclusions, department capacity and one-department-per-day, which is enough
// to exercise every UI state. It is NOT the scheduling algorithm.
// ---------------------------------------------------------------------------

export function buildWeek(weekStart: string): ScheduleWeek {
  const cells: ScheduleCell[] = []
  const hours = new Map<number, number>()

  const shiftsLeft = (s: Staff) =>
    Math.floor((s.contract_hours - (hours.get(s.id) ?? 0)) / 4)

  DAYS.forEach((day, dayIndex) => {
    // A staff member works ONE department for the whole day (app.py:229-245),
    // so the day's roster has to be split across departments up front —
    // assigning greedily department by department starves the last one.
    const pool = staff
      .filter((s) => !s.day_exclusions.includes(day))
      .filter((s) => shiftsLeft(s) > 0)
      .sort((a, b) => (hours.get(a.id) ?? 0) - (hours.get(b.id) ?? 0))

    // Rotate the starting department each day so the same one isn't always
    // first in line for the freshest staff.
    const order = departments.map(
      (_, i) => departments[(i + dayIndex) % departments.length],
    )

    const roster = new Map<number, Staff[]>(order.map((d) => [d.id, []]))
    let cursor = 0

    // Round 1: everyone gets their minimum. Round 2: top up toward max.
    for (const dept of order) {
      for (let i = 0; i < dept.min_staff && cursor < pool.length; i++) {
        roster.get(dept.id)!.push(pool[cursor++])
      }
    }
    for (const dept of order) {
      const list = roster.get(dept.id)!
      while (list.length < dept.max_staff && cursor < pool.length) {
        list.push(pool[cursor++])
      }
    }

    for (const dept of departments) {
      const dayStaff = roster.get(dept.id) ?? []

      for (const shift of SHIFTS) {
        // Mornings only need the department minimum; later shifts aim for max.
        // Mirrors target_capacity() described in readme.md.
        const target =
          shift === 'morning' ? dept.min_staff : dept.max_staff

        // One deliberately short cell so the understaffed path is reachable.
        const cap =
          dept.name === 'Cashier' &&
          shift === 'evening' &&
          day === 'monday'
            ? Math.max(0, dept.min_staff - 1)
            : target

        const picked = dayStaff
          .filter((s) => !s.shift_exclusions.includes(shift))
          .filter((s) => shiftsLeft(s) > 0)
          .sort((a, b) => (hours.get(a.id) ?? 0) - (hours.get(b.id) ?? 0))
          .slice(0, cap)

        for (const s of picked) {
          hours.set(s.id, (hours.get(s.id) ?? 0) + 4)
        }

        cells.push({
          department_id: dept.id,
          day,
          shift,
          staff: picked.map((s) => ({
            staff_id: s.id,
            staff_name: `${s.first_name} ${s.last_name}`,
          })),
        })
      }
    }
  })

  return {
    week_start: weekStart,
    week_end: weekEnd(weekStart),
    generated_at: new Date().toISOString(),
    cells,
  }
}

/** Seed the current week so the app has something to show on first load. */
weeks.set(currentWeekStart(), buildWeek(currentWeekStart()))
