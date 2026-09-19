import type { Day, Position, Shift } from './common'

/** What the staff portal shows about the person it's open for. */
export interface PortalProfile {
  id: number
  first_name: string
  last_name: string
  email: string
  position: Position
  contract_hours: number
  min_hours: number
  day_exclusions: Day[]
  shift_exclusions: Shift[]
  /** False until they've set a password from their invite link. */
  has_account: boolean
}

export interface PortalShift {
  /** ISO date. */
  date: string
  day: Day
  shift: Shift
  department_id: number
  department_name: string
}

export interface PortalWeek {
  week_start: string
  week_end: string
  /** False when the manager hasn't generated a rota for this week yet. */
  published: boolean
  hours: number
  shifts: PortalShift[]
}

export interface PortalWeekArgs {
  weekStart: string
  /** Admins pick whose portal to view; staff always see their own. */
  staffId?: number
}

/** Whether a staff email already has a password (create vs sign in). */
export interface AccountStatus {
  has_account: boolean
}

// Invite links — disabled while staff emails are placeholders.
// export interface Invite {
//   token: string
//   expires_at: string
// }
//
// export interface InviteDetails {
//   first_name: string
//   last_name: string
//   email: string
// }
