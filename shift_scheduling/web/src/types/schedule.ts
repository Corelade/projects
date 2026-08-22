import type { Day, Shift } from './common'

export interface Assignment {
  staff_id: number
  /** Denormalised for display so a cell never needs a join. */
  staff_name: string
}

/** One (department, shift, day) — the atom the grid renders and edits. */
export interface ScheduleCell {
  department_id: number
  day: Day
  shift: Shift
  staff: Assignment[]
}

export interface ScheduleWeek {
  /** ISO date, always a Monday. */
  week_start: string
  week_end: string
  generated_at: string | null
  cells: ScheduleCell[]
}

export interface GenerateRequest {
  week_start: string
}

export interface UpdateCellRequest {
  week_start: string
  department_id: number
  day: Day
  shift: Shift
  staff_ids: number[]
}

/** Why a staff member can't take a cell — surfaced in the picker and on pills. */
export type ConflictReason =
  | 'day_excluded'
  | 'shift_excluded'
  | 'booked_elsewhere'
  | 'over_contract'

export interface Conflict {
  staff_id: number
  reason: ConflictReason
  message: string
}
