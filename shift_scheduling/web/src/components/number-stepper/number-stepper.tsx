import { cn } from '@/lib/cn'
import Icon from '@/components/icon/icon'

export interface NumberStepperProps {
  id?: string
  value: number | ''
  onChange: (value: number | '') => void
  min?: number
  max?: number
  step?: number
  suffix?: string
  invalid?: boolean
  disabled?: boolean
  'aria-describedby'?: string
}

/**
 * Typing an out-of-range value shows the error state rather than silently
 * correcting; the steppers themselves clamp (docs/ui/03-components.md).
 */
export default function NumberStepper({
  id,
  value,
  onChange,
  min = 0,
  max = 999,
  step = 1,
  suffix,
  invalid,
  disabled,
  ...aria
}: NumberStepperProps) {
  const current = value === '' ? min : value
  const clamp = (n: number) => Math.min(max, Math.max(min, n))

  return (
    <div
      className={cn(
        'flex h-(--size-control) w-full items-stretch overflow-hidden rounded-md border bg-surface',
        'transition-colors duration-(--duration-fast)',
        // The inner input suppresses its own outline, so the wrapper carries
        // the focus treatment — never outline:none without a replacement.
        'has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-brand-500',
        invalid ? 'border-danger-600' : 'border-border hover:border-border-strong',
        disabled && 'cursor-not-allowed bg-surface-subtle',
      )}
    >
      <button
        type="button"
        aria-label="Decrease"
        disabled={disabled || current <= min}
        onClick={() => onChange(clamp(current - step))}
        className="focus-ring flex w-9 shrink-0 items-center justify-center text-fg-muted hover:bg-surface-subtle hover:text-fg disabled:cursor-not-allowed disabled:text-fg-subtle disabled:hover:bg-transparent"
      >
        <Icon name="minus" size={16} />
      </button>

      <div className="flex flex-1 items-center justify-center gap-1 border-x border-border px-2">
        <input
          {...aria}
          id={id}
          type="text"
          inputMode="numeric"
          value={value}
          disabled={disabled}
          aria-invalid={invalid || undefined}
          onChange={(e) => {
            const raw = e.target.value.trim()
            if (raw === '') return onChange('')
            if (!/^\d+$/.test(raw)) return
            onChange(Number(raw))
          }}
          className="tabular w-full bg-transparent text-center text-body text-fg outline-none disabled:cursor-not-allowed disabled:text-fg-subtle"
        />
        {suffix && <span className="shrink-0 text-small text-fg-muted">{suffix}</span>}
      </div>

      <button
        type="button"
        aria-label="Increase"
        disabled={disabled || current >= max}
        onClick={() => onChange(clamp(current + step))}
        className="focus-ring flex w-9 shrink-0 items-center justify-center text-fg-muted hover:bg-surface-subtle hover:text-fg disabled:cursor-not-allowed disabled:text-fg-subtle disabled:hover:bg-transparent"
      >
        <Icon name="plus" size={16} />
      </button>
    </div>
  )
}
