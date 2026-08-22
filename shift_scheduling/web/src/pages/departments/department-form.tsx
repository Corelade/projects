import { useMemo, useState } from 'react'

import Field from '@/components/field/field'
import Input from '@/components/input/input'
import NumberStepper from '@/components/number-stepper/number-stepper'
import {
  hasErrors,
  validateDepartment,
  type Errors,
} from '@/lib/validation'
import { DAYS, HOURS_PER_DAY, type Department, type DepartmentInput } from '@/types'

const EMPTY_DEPARTMENT: DepartmentInput = {
  name: '',
  min_staff: 1,
  max_staff: 3,
}

export const DEPARTMENT_FORM_ID = 'department-form'

export interface DepartmentFormProps {
  initial?: Department
  submitting: boolean
  serverErrors: Errors<DepartmentInput>
  onSubmit: (value: DepartmentInput) => void
  onDirtyChange: (dirty: boolean) => void
}

export default function DepartmentForm({
  initial,
  submitting,
  serverErrors,
  onSubmit,
  onDirtyChange,
}: DepartmentFormProps) {
  const [value, setValue] = useState<DepartmentInput>(
    initial ? { ...initial } : { ...EMPTY_DEPARTMENT },
  )
  const [touched, setTouched] = useState<Set<keyof DepartmentInput>>(new Set())
  const [submitted, setSubmitted] = useState(false)

  const clientErrors = useMemo(() => validateDepartment(value), [value])
  const errors: Errors<DepartmentInput> = { ...clientErrors, ...serverErrors }

  const errorFor = (key: keyof DepartmentInput) =>
    submitted || touched.has(key) ? errors[key] : undefined

  function patch<K extends keyof DepartmentInput>(key: K, next: DepartmentInput[K]) {
    setValue((v) => ({ ...v, [key]: next }))
    onDirtyChange(true)
  }

  const markTouched = (key: keyof DepartmentInput) =>
    setTouched((t) => new Set(t).add(key))

  /** Minimum coverage this department demands across the week. */
  const staffShifts =
    (Number(value.min_staff) || 0) * (HOURS_PER_DAY / 4) * DAYS.length

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitted(true)
    if (hasErrors(clientErrors)) return
    onSubmit(value)
  }

  return (
    <form id={DEPARTMENT_FORM_ID} onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Field
        id="name"
        label="Department name"
        required
        error={errorFor('name')}
      >
        {(p) => (
          <Input
            {...p}
            value={value.name}
            placeholder="Shoes"
            disabled={submitting}
            invalid={Boolean(errorFor('name'))}
            onChange={(e) => patch('name', e.target.value)}
            onBlur={() => markTouched('name')}
          />
        )}
      </Field>

      <div className="grid grid-cols-2 gap-3">
        <Field
          id="min_staff"
          label="Min staff"
          hint="Required cover"
          error={errorFor('min_staff')}
        >
          {(p) => (
            <NumberStepper
              {...p}
              value={value.min_staff}
              min={1}
              max={20}
              disabled={submitting}
              invalid={Boolean(errorFor('min_staff'))}
              onChange={(n) => {
                patch('min_staff', (n === '' ? 0 : n) as number)
                markTouched('min_staff')
              }}
            />
          )}
        </Field>

        <Field
          id="max_staff"
          label="Max staff"
          hint="Target cover"
          error={errorFor('max_staff')}
        >
          {(p) => (
            <NumberStepper
              {...p}
              value={value.max_staff}
              min={1}
              max={20}
              disabled={submitting}
              invalid={Boolean(errorFor('max_staff'))}
              onChange={(n) => {
                patch('max_staff', (n === '' ? 0 : n) as number)
                markTouched('max_staff')
              }}
            />
          )}
        </Field>
      </div>

      <p className="tabular rounded-md bg-surface-subtle px-3 py-2 text-small text-fg-muted">
        Needs at least {staffShifts} staff-shifts per week.
      </p>

    </form>
  )
}
