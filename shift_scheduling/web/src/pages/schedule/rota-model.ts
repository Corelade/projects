/**
 * Derivations over a week. Kept out of components so the grid, the picker and
 * the PDF all read the same numbers.
 */

import { HOURS_PER_SHIFT, type Day, type Department, type ScheduleCell, type ScheduleWeek, type Shift, type Staff } from '@/types'

export const cellKey = (departmentId: number, day: Day, shift: Shift) =>
  `${departmentId}:${day}:${shift}`

export function indexCells(week: ScheduleWeek | undefined) {
  const map = new Map<string, ScheduleCell>()
  for (const cell of week?.cells ?? []) {
    map.set(cellKey(cell.department_id, cell.day, cell.shift), cell)
  }
  return map
}

/** Hours each staff member is booked for across the whole week. */
export function hoursByStaff(week: ScheduleWeek | undefined) {
  const hours = new Map<number, number>()
  for (const cell of week?.cells ?? []) {
    for (const a of cell.staff) {
      hours.set(a.staff_id, (hours.get(a.staff_id) ?? 0) + HOURS_PER_SHIFT)
    }
  }
  return hours
}

/** Which department each staff member is tied to on a given day, if any. */
export function departmentByStaffDay(week: ScheduleWeek | undefined) {
  const map = new Map<string, number>()
  for (const cell of week?.cells ?? []) {
    for (const a of cell.staff) {
      map.set(`${a.staff_id}:${cell.day}`, cell.department_id)
    }
  }
  return map
}

export type Coverage = 'under' | 'at-min' | 'ok' | 'empty'

export function coverageOf(count: number, department: Department): Coverage {
  if (count === 0) return department.min_staff > 0 ? 'under' : 'empty'
  if (count < department.min_staff) return 'under'
  if (count === department.min_staff) return 'at-min'
  return 'ok'
}

export interface Availability {
  available: boolean
  reason?: string
}

/**
 * Why a staff member can or can't take a cell. Mirrors is_valid() in
 * app.py:261-347: exclusions, one department per day, and contract hours.
 */
export function availabilityFor(
  staff: Staff,
  opts: {
    day: Day
    shift: Shift
    departmentId: number
    hours: Map<number, number>
    dayDepartment: Map<string, number>
    alreadyInCell: boolean
  },
): Availability {
  if (opts.alreadyInCell) return { available: true }

  if (staff.day_exclusions.includes(opts.day)) {
    const day = opts.day.charAt(0).toUpperCase() + opts.day.slice(1)
    return { available: false, reason: `Not available on ${day}s` }
  }
  if (staff.shift_exclusions.includes(opts.shift)) {
    return { available: false, reason: `Not available on ${opts.shift}s` }
  }

  const tied = opts.dayDepartment.get(`${staff.id}:${opts.day}`)
  if (tied !== undefined && tied !== opts.departmentId) {
    return { available: false, reason: 'Already working another department that day' }
  }

  const worked = opts.hours.get(staff.id) ?? 0
  if (worked + HOURS_PER_SHIFT > staff.contract_hours) {
    return {
      available: false,
      reason: `Would exceed their ${staff.contract_hours}h contract`,
    }
  }

  return { available: true }
}
