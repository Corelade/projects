import type { Day } from '@/types'
import { DAYS } from '@/types'

/** Weeks run Monday->Sunday to match DAY_OF_WEEK in app.py. */

const MS_PER_DAY = 86_400_000

export function toISODate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export function fromISODate(iso: string): Date {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y, m - 1, d)
}

/** The Monday of the week containing `date`. */
export function startOfWeek(date: Date): Date {
  const d = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  // getDay(): 0=Sun..6=Sat. Shift so Monday is 0.
  const offset = (d.getDay() + 6) % 7
  d.setDate(d.getDate() - offset)
  return d
}

export function currentWeekStart(): string {
  return toISODate(startOfWeek(new Date()))
}

export function addWeeks(weekStart: string, delta: number): string {
  const d = fromISODate(weekStart)
  d.setDate(d.getDate() + delta * 7)
  return toISODate(d)
}

export function weekEnd(weekStart: string): string {
  const d = fromISODate(weekStart)
  d.setDate(d.getDate() + 6)
  return toISODate(d)
}

/** Date of a given weekday within the week starting `weekStart`. */
export function dateOfDay(weekStart: string, day: Day): Date {
  const d = fromISODate(weekStart)
  d.setDate(d.getDate() + DAYS.indexOf(day))
  return d
}

export function isCurrentWeek(weekStart: string): boolean {
  return weekStart === currentWeekStart()
}

/** "17 – 23 Aug 2026", collapsing repeated month and year. */
export function formatWeekRange(weekStart: string): string {
  const start = fromISODate(weekStart)
  const end = fromISODate(weekEnd(weekStart))

  const sameMonth = start.getMonth() === end.getMonth()
  const sameYear = start.getFullYear() === end.getFullYear()

  const month = (d: Date) => d.toLocaleDateString('en-GB', { month: 'short' })

  if (sameMonth && sameYear) {
    return `${start.getDate()} – ${end.getDate()} ${month(end)} ${end.getFullYear()}`
  }
  if (sameYear) {
    return `${start.getDate()} ${month(start)} – ${end.getDate()} ${month(end)} ${end.getFullYear()}`
  }
  return `${start.getDate()} ${month(start)} ${start.getFullYear()} – ${end.getDate()} ${month(end)} ${end.getFullYear()}`
}

/** "Mon 17" for a grid column header. */
export function formatDayHeader(weekStart: string, day: Day): string {
  const d = dateOfDay(weekStart, day)
  const label = d.toLocaleDateString('en-GB', { weekday: 'short' })
  return `${label} ${d.getDate()}`
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function daysBetween(a: string, b: string): number {
  return Math.round((fromISODate(b).getTime() - fromISODate(a).getTime()) / MS_PER_DAY)
}
