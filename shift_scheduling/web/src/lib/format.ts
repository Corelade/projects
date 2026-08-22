import type { Day, Shift, Staff } from '@/types'

export function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export function fullName(s: Pick<Staff, 'first_name' | 'last_name'>): string {
  return `${s.first_name} ${s.last_name}`.trim()
}

export function initials(s: Pick<Staff, 'first_name' | 'last_name'>): string {
  return `${s.first_name.charAt(0)}${s.last_name.charAt(0)}`.toUpperCase()
}

const DAY_SHORT: Record<Day, string> = {
  monday: 'Mon',
  tuesday: 'Tue',
  wednesday: 'Wed',
  thursday: 'Thu',
  friday: 'Fri',
  saturday: 'Sat',
  sunday: 'Sun',
}

const SHIFT_SHORT: Record<Shift, string> = {
  morning: 'AM',
  afternoon: 'PM',
  evening: 'EVE',
}

export const dayShort = (d: Day) => DAY_SHORT[d]
export const shiftShort = (s: Shift) => SHIFT_SHORT[s]

/** "Wed, Sat · PM" — compact exclusion summary for the staff table. */
export function summariseExclusions(
  days: Day[],
  shifts: Shift[],
): string {
  const parts: string[] = []
  if (days.length) parts.push(days.map(dayShort).join(', '))
  if (shifts.length) parts.push(shifts.map(shiftShort).join(', '))
  return parts.length ? parts.join(' · ') : '—'
}
