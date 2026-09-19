import type { Day, Shift } from './common'

export type RequestStatus = 'pending' | 'approved' | 'rejected' | 'cancelled'

/** A staff member asking to change their availability. Holds the full requested state. */
export interface AvailabilityRequest {
  id: number
  staff_id: number
  staff_name: string
  status: RequestStatus
  day_exclusions: Day[]
  shift_exclusions: Shift[]
  /** Their availability right now, to compare against. */
  current_day_exclusions: Day[]
  current_shift_exclusions: Shift[]
  note: string | null
  admin_note: string | null
  created_at: string
  reviewed_at: string | null
}

export interface AvailabilityRequestInput {
  day_exclusions: Day[]
  shift_exclusions: Shift[]
  note?: string
}

/** Leave the exclusions out to approve as requested; send them to approve with changes. */
export interface ApproveRequestArgs {
  id: number
  day_exclusions?: Day[]
  shift_exclusions?: Shift[]
  admin_note?: string
}

export interface RejectRequestArgs {
  id: number
  admin_note?: string
}

export type NotificationKind =
  | 'availability_requested'
  | 'availability_approved'
  | 'availability_rejected'
  | 'availability_updated'

export interface AppNotification {
  id: number
  kind: NotificationKind
  message: string
  request_id: number | null
  read: boolean
  created_at: string
}

export interface NotificationList {
  unread: number
  /** The latest 20. */
  items: AppNotification[]
}
