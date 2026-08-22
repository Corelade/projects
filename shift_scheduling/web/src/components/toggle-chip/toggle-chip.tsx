import { cn } from '@/lib/cn'
import Icon from '@/components/icon/icon'

export interface ToggleChipProps {
  value: string
  label: string
  checked: boolean
  onChange: (value: string) => void
  disabled?: boolean
  name?: string
}

/**
 * A real checkbox, visually hidden, presented as a compact pill — so keyboard,
 * screen readers and form semantics all work while taking ~2 rows instead of 8.
 * Selection carries a check glyph as well as fill: never colour alone.
 */
export default function ToggleChip({
  value,
  label,
  checked,
  onChange,
  disabled,
  name,
}: ToggleChipProps) {
  return (
    <label
      className={cn(
        'inline-flex cursor-pointer select-none items-center gap-1.5 rounded-sm border px-3 py-1.5 text-small font-medium',
        'transition-colors duration-(--duration-fast)',
        'has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-brand-500',
        checked
          ? 'border-brand-200 bg-brand-100 text-brand-700'
          : 'border-border bg-surface text-fg-muted hover:bg-surface-subtle hover:text-fg',
        disabled && 'cursor-not-allowed opacity-60 hover:bg-surface',
      )}
    >
      <input
        type="checkbox"
        name={name}
        value={value}
        checked={checked}
        disabled={disabled}
        onChange={() => onChange(value)}
        className="sr-only"
      />
      {checked && <Icon name="check" size={16} className="shrink-0" />}
      {label}
    </label>
  )
}
