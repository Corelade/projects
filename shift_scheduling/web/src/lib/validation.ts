/**
 * Client-side mirrors of the domain rules in classes.py.
 * The server stays the authority — these only pre-empt round trips.
 * See docs/ui/04-patterns.md.
 */

import type { Day, DepartmentInput, Shift, StaffInput } from '@/types'
import { HOURS_PER_DAY, HOURS_PER_SHIFT, DAYS } from '@/types'

export const MIN_CONTRACT_HOURS = 8
export const MAX_CONTRACT_HOURS = 40

export type Errors<T> = Partial<Record<keyof T, string>>

/**
 * classes.py:96-113 — a person whose exclusions leave them fewer available
 * hours than their contract can never be scheduled. Catch it at entry time
 * rather than letting the whole solve fail with no obvious cause.
 */
export function availableHours(
  dayExclusions: Day[],
  shiftExclusions: Shift[],
): number {
  const hoursPerDay = HOURS_PER_DAY - HOURS_PER_SHIFT * shiftExclusions.length
  const days = DAYS.length - dayExclusions.length
  return Math.max(0, hoursPerDay * days)
}

export const MAX_POSSIBLE_HOURS = HOURS_PER_DAY * DAYS.length // 84

export function validateStaff(input: StaffInput): Errors<StaffInput> {
  const errors: Errors<StaffInput> = {}

  if (!input.first_name.trim()) errors.first_name = 'First name is required.'
  if (!input.last_name.trim()) errors.last_name = 'Last name is required.'

  if (!input.email.trim()) {
    errors.email = 'Email is required.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email.trim())) {
    errors.email = 'Enter a valid email address.'
  }

  const contract = Number(input.contract_hours)
  if (!Number.isFinite(contract) || contract < MIN_CONTRACT_HOURS || contract > MAX_CONTRACT_HOURS) {
    errors.contract_hours = `Contract hours must be between ${MIN_CONTRACT_HOURS} and ${MAX_CONTRACT_HOURS}.`
  }

  const min = Number(input.min_hours)
  if (!Number.isFinite(min) || min < MIN_CONTRACT_HOURS) {
    errors.min_hours = `Minimum hours must be at least ${MIN_CONTRACT_HOURS}.`
  } else if (Number.isFinite(contract) && min > contract) {
    errors.min_hours = "Minimum hours can't exceed contract hours."
  }

  const available = availableHours(input.day_exclusions, input.shift_exclusions)
  if (Number.isFinite(contract) && available < contract) {
    errors.shift_exclusions = `These exclusions leave only ${available} hours available — not enough for a ${contract}-hour contract.`
  }

  return errors
}

export function validateDepartment(
  input: DepartmentInput,
): Errors<DepartmentInput> {
  const errors: Errors<DepartmentInput> = {}

  if (!input.name.trim()) {
    errors.name = 'Department name is required.'
  }

  const min = Number(input.min_staff)
  const max = Number(input.max_staff)

  if (!Number.isFinite(min) || min < 1) {
    errors.min_staff = 'Minimum staff must be at least 1.'
  }
  if (!Number.isFinite(max) || max < 1) {
    errors.max_staff = 'Maximum staff must be at least 1.'
  } else if (Number.isFinite(min) && min > max) {
    errors.max_staff = "Maximum staff can't be less than minimum staff."
  }

  return errors
}

export function hasErrors<T>(errors: Errors<T>): boolean {
  return Object.keys(errors).length > 0
}
