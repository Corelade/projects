import { useMemo, useState } from 'react'

import Field from '@/components/field/field'
import Input from '@/components/input/input'
import NumberStepper from '@/components/number-stepper/number-stepper'
import Select from '@/components/select/select'
import ToggleChipGroup from '@/components/toggle-chip/toggle-chip-group'
import { capitalize } from '@/lib/format'
import {
  availableHours,
  hasErrors,
  MAX_CONTRACT_HOURS,
  MAX_POSSIBLE_HOURS,
  MIN_CONTRACT_HOURS,
  validateStaff,
  type Errors,
} from '@/lib/validation'
import type { Day, Position, Shift, Staff, StaffInput } from '@/types'
import { DAYS, POSITION_LABELS, POSITIONS, SHIFTS } from '@/types'

const EMPTY_STAFF: StaffInput = {
  first_name: '',
  last_name: '',
  email: '',
  position: 'associate', // documented default
  contract_hours: 40,
  min_hours: 8,
  day_exclusions: [],
  shift_exclusions: [],
}

export const STAFF_FORM_ID = 'staff-form'

export interface StaffFormProps {
  initial?: Staff
  submitting: boolean
  serverErrors: Errors<StaffInput>
  onSubmit: (value: StaffInput) => void
  onDirtyChange: (dirty: boolean) => void
}

export default function StaffForm({
  initial,
  submitting,
  serverErrors,
  onSubmit,
  onDirtyChange,
}: StaffFormProps) {
  const [value, setValue] = useState<StaffInput>(
    initial ? { ...initial } : { ...EMPTY_STAFF },
  )
  const [touched, setTouched] = useState<Set<keyof StaffInput>>(new Set())
  const [submitted, setSubmitted] = useState(false)

  const clientErrors = useMemo(() => validateStaff(value), [value])
  const errors: Errors<StaffInput> = { ...clientErrors, ...serverErrors }

  /** Show an error once the field has been left, or once submit was attempted. */
  const errorFor = (key: keyof StaffInput) =>
    submitted || touched.has(key) ? errors[key] : undefined

  function patch<K extends keyof StaffInput>(key: K, next: StaffInput[K]) {
    setValue((v) => ({ ...v, [key]: next }))
    onDirtyChange(true)
  }

  const markTouched = (key: keyof StaffInput) =>
    setTouched((t) => new Set(t).add(key))

  function toggle<T extends string>(key: 'day_exclusions' | 'shift_exclusions', option: T) {
    setValue((v) => {
      const list = v[key] as string[]
      const next = list.includes(option)
        ? list.filter((x) => x !== option)
        : [...list, option]
      return { ...v, [key]: next }
    })
    onDirtyChange(true)
    markTouched(key)
  }

  const available = availableHours(value.day_exclusions, value.shift_exclusions)
  const contract = Number(value.contract_hours) || 0
  const availabilityShort = available < contract

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitted(true)
    if (hasErrors(clientErrors)) return
    onSubmit(value)
  }

  return (
    <form id={STAFF_FORM_ID} onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Field id="first_name" label="First name" required error={errorFor('first_name')}>
          {(p) => (
            <Input
              {...p}
              value={value.first_name}
              placeholder="John"
              disabled={submitting}
              invalid={Boolean(errorFor('first_name'))}
              onChange={(e) => patch('first_name', e.target.value)}
              onBlur={() => markTouched('first_name')}
            />
          )}
        </Field>

        <Field id="last_name" label="Last name" required error={errorFor('last_name')}>
          {(p) => (
            <Input
              {...p}
              value={value.last_name}
              placeholder="Adeyemi"
              disabled={submitting}
              invalid={Boolean(errorFor('last_name'))}
              onChange={(e) => patch('last_name', e.target.value)}
              onBlur={() => markTouched('last_name')}
            />
          )}
        </Field>
      </div>

      <Field
        id="email"
        label="Email"
        required
        hint={initial ? "Email can't be changed after creation." : undefined}
        error={errorFor('email')} >
        {(p) => (
          <Input
            {...p}
            type="email"
            value={value.email}
            placeholder="john@example.com"
            disabled={submitting || Boolean(initial)}
            invalid={Boolean(errorFor('email'))}
            onChange={(e) => patch('email', e.target.value)}
            onBlur={() => markTouched('email')}
          />
        )}
      </Field>

      <Field id="position" label="Position" error={errorFor('position')}>
        {(p) => (
          <Select
            {...p}
            value={value.position}
            disabled={submitting}
            onChange={(e) => patch('position', e.target.value as Position)}
          >
            {POSITIONS.map((pos) => (
              <option key={pos} value={pos}>
                {POSITION_LABELS[pos]}
              </option>
            ))}
          </Select>
        )}
      </Field>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Field
          id="contract_hours"
          label="Contract hours"
          hint="Per week"
          error={errorFor('contract_hours')}
        >
          {(p) => (
            <NumberStepper
              {...p}
              value={value.contract_hours}
              min={MIN_CONTRACT_HOURS}
              max={MAX_CONTRACT_HOURS}
              step={4}
              suffix="h"
              disabled={submitting}
              invalid={Boolean(errorFor('contract_hours'))}
              onChange={(n) => {
                patch('contract_hours', (n === '' ? 0 : n) as number)
                markTouched('contract_hours')
              }}
            />
          )}
        </Field>

        <Field
          id="min_hours"
          label="Minimum hours"
          hint="Must work at least"
          error={errorFor('min_hours')}
        >
          {(p) => (
            <NumberStepper
              {...p}
              value={value.min_hours}
              min={MIN_CONTRACT_HOURS}
              max={MAX_CONTRACT_HOURS}
              step={4}
              suffix="h"
              disabled={submitting}
              invalid={Boolean(errorFor('min_hours'))}
              onChange={(n) => {
                patch('min_hours', (n === '' ? 0 : n) as number)
                markTouched('min_hours')
              }}
            />
          )}
        </Field>
      </div>

      <ToggleChipGroup<Day>
        id="day_exclusions"
        label="Days not available"
        options={DAYS}
        selected={value.day_exclusions}
        onToggle={(d) => toggle('day_exclusions', d)}
        renderLabel={(d) => capitalize(d).slice(0, 3)}
        disabled={submitting}
      />

      <ToggleChipGroup<Shift>
        id="shift_exclusions"
        label="Shifts not available"
        options={SHIFTS}
        selected={value.shift_exclusions}
        onToggle={(s) => toggle('shift_exclusions', s)}
        renderLabel={(s) => capitalize(s)}
        disabled={submitting}
        error={errorFor('shift_exclusions')}
      />

      {/*
        classes.py:96-113 — catches "this person can't physically work their
        contract" at entry time rather than at solve time.
      */}
      {!availabilityShort && (
        <p className="tabular rounded-md bg-surface-subtle px-3 py-2 text-small text-fg-muted">
          {available} of {MAX_POSSIBLE_HOURS} possible hours available.
        </p>
      )}

    </form>
  )
}
