import { cn } from '@/lib/cn'
import { capitalize } from '@/lib/format'
import { DAYS, SHIFTS } from '@/types'

export interface AvailabilityDiffProps {
  currentDays: string[]
  currentShifts: string[]
  days: string[]
  shifts: string[]
}

/**
 * Current vs requested "can't work" days and shifts, as one row of chips each.
 * A chip that changes is marked, so a reviewer sees the ask at a glance.
 */
export default function AvailabilityDiff({
  currentDays,
  currentShifts,
  days,
  shifts,
}: AvailabilityDiffProps) {
  return (
    <div className="flex flex-col gap-2">
      <DiffRow
        label="Can't work (days)"
        options={DAYS}
        current={currentDays}
        next={days}
        short
      />
      <DiffRow
        label="Can't work (shifts)"
        options={SHIFTS}
        current={currentShifts}
        next={shifts}
      />
      <p className="flex flex-wrap gap-x-4 gap-y-1 text-caption text-fg-muted">
        <Legend className="border-danger-200 bg-danger-50 text-danger-700">+ newly unavailable</Legend>
        <Legend className="border-success-200 bg-success-50 text-success-700">− available again</Legend>
        <Legend className="border-border bg-surface-subtle text-fg-muted">unchanged</Legend>
      </p>
    </div>
  )
}

function DiffRow({
  label,
  options,
  current,
  next,
  short,
}: {
  label: string
  options: readonly string[]
  current: string[]
  next: string[]
  short?: boolean
}) {
  return (
    <div className="flex flex-col gap-1">
      <span className="caption">{label}</span>
      <div className="flex flex-wrap gap-1.5">
        {options.map((o) => {
          const was = current.includes(o)
          const now = next.includes(o)
          if (!was && !now) return null
          const text = short ? capitalize(o).slice(0, 3) : capitalize(o)
          return (
            <span
              key={o}
              className={cn(
                'inline-flex items-center rounded-sm border px-2 py-0.5 text-caption font-medium',
                was && now && 'border-border bg-surface-subtle text-fg-muted',
                !was && now && 'border-danger-200 bg-danger-50 text-danger-700',
                was && !now && 'border-success-200 bg-success-50 text-success-700 line-through',
              )}
            >
              {!was && now ? '+ ' : was && !now ? '− ' : ''}
              {text}
            </span>
          )
        })}
        {!current.length && !next.length && (
          <span className="text-small text-fg-subtle">None</span>
        )}
      </div>
    </div>
  )
}

function Legend({ className, children }: { className: string; children: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={cn('size-3 rounded-sm border', className)} />
      {children}
    </span>
  )
}
