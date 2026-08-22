import type { Day, Position, Shift } from './common'

export interface Staff {
  id: number
  first_name: string
  last_name: string
  email: string
  position: Position
  /** Weekly contract hours, 8–40. */
  contract_hours: number
  /** Minimum hours to work in the week; 8 <= min_hours <= contract_hours. */
  min_hours: number
  /** "Days not available". */
  day_exclusions: Day[]
  /** "Shifts not available". */
  shift_exclusions: Shift[]
}

export type StaffInput = Omit<Staff, 'id'>
