import ToggleChip from './toggle-chip'

export interface ToggleChipGroupProps<T extends string> {
  label: string
  options: readonly T[]
  selected: T[]
  onToggle: (value: T) => void
  renderLabel: (value: T) => string
  disabled?: boolean
  error?: string
  hint?: string
  id: string
}

export default function ToggleChipGroup<T extends string>({
  label,
  options,
  selected,
  onToggle,
  renderLabel,
  disabled,
  error,
  hint,
  id,
}: ToggleChipGroupProps<T>) {
  return (
    <div role="group" aria-labelledby={`${id}-label`} className="flex flex-col gap-1.5">
      <span id={`${id}-label`} className="caption">
        {label}
      </span>

      <div className="flex flex-wrap gap-1.5">
        {options.map((option) => (
          <ToggleChip
            key={option}
            name={id}
            value={option}
            label={renderLabel(option)}
            checked={selected.includes(option)}
            onChange={() => onToggle(option)}
            disabled={disabled}
          />
        ))}
      </div>

      {error ? (
        <p className="text-small text-danger-700">{error}</p>
      ) : hint ? (
        <p className="text-small text-fg-muted">{hint}</p>
      ) : null}
    </div>
  )
}
