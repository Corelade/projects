import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export interface FieldProps {
  id: string
  label: string
  hint?: string
  error?: string
  required?: boolean
  className?: string
  children: (props: {
    id: string
    'aria-describedby'?: string
    'aria-invalid'?: boolean
  }) => ReactNode
}

/**
 * Label -> control -> hint OR error. Error replaces hint; they never both show.
 */
export default function Field({
  id,
  label,
  hint,
  error,
  required,
  className,
  children,
}: FieldProps) {
  const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <label htmlFor={id} className="caption">
        {label}
        {required && <span className="text-danger-600"> *</span>}
      </label>

      {children({
        id,
        'aria-describedby': describedBy,
        'aria-invalid': error ? true : undefined,
      })}

      {error ? (
        <p id={`${id}-error`} className="text-small text-danger-700">
          {error}
        </p>
      ) : hint ? (
        <p id={`${id}-hint`} className="text-small text-fg-muted">
          {hint}
        </p>
      ) : null}
    </div>
  )
}
