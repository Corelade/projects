/** Wire values are lowercase to match DAY_OF_WEEK / shift_time in app.py:9-18. */

export const DAYS = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
] as const
export type Day = (typeof DAYS)[number]

export const SHIFTS = ['morning', 'afternoon', 'evening'] as const
export type Shift = (typeof SHIFTS)[number]

export const POSITIONS = ['associate', 'management', 'loss_protection'] as const
export type Position = (typeof POSITIONS)[number]

export const POSITION_LABELS: Record<Position, string> = {
  associate: 'Associate',
  management: 'Management',
  loss_protection: 'Loss protection',
}

/** Each shift is four hours; a department is open twelve hours a day. */
export const HOURS_PER_SHIFT = 4
export const HOURS_PER_DAY = HOURS_PER_SHIFT * SHIFTS.length

export interface ApiError {
  status: number
  message: string
  /** Field-level errors keyed by field name, when the server sends them. */
  fields?: Record<string, string>
}
