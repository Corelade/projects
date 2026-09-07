import Icon from '@/components/icon/icon'
import { cn } from '@/lib/cn'
import { SHIFTS } from '@/types'
import { capitalize } from '@/lib/format'

/** Four days is enough to read the pattern; seven would only shrink the cells. */
const DAYS = ['Mon 17', 'Tue 18', 'Wed 19', 'Thu 20']

const TINT: Record<string, string> = {
  morning: 'bg-shift-morning-bg',
  afternoon: 'bg-shift-afternoon-bg',
  evening: 'bg-shift-evening-bg',
}

/**
 * A still of the real grid, not a screenshot — same shift tints, same headcount
 * text, same under-staffed treatment, so what the page promises is what the
 * product does. Purely decorative: the prose beside it carries the meaning.
 */
const CELLS: Record<string, { names: string[]; count: string; under?: boolean }[]> = {
  morning: [
    { names: ['Riri O.', 'Core S.'], count: '2/3' },
    { names: ['Shem B.', 'Tayo A.'], count: '2/3' },
    { names: ['Riri O.', 'Lanre B.'], count: '2/3' },
    { names: ['Chidi U.', 'Jide F.'], count: '2/3' },
  ],
  afternoon: [
    { names: ['Lanre B.', 'Riri O.', 'Core S.'], count: '3/3' },
    { names: ['Chidi U.', 'Shem B.', 'Tayo A.'], count: '3/3' },
    { names: ['Loli N.', 'Riri O.', 'Lanre B.'], count: '3/3' },
    { names: ['Loli N.', 'Chidi U.', 'Jide F.'], count: '3/3' },
  ],
  evening: [
    { names: ['Lanre B.'], count: '1/3', under: true },
    { names: ['Chidi U.', 'Shem B.'], count: '2/3' },
    { names: ['Riri O.', 'Lanre B.'], count: '2/3' },
    { names: ['Chidi U.'], count: '1/3', under: true },
  ],
}

export default function RotaPreview() {
  return (
    <div
      aria-hidden="true"
      className="overflow-hidden rounded-lg border border-border bg-surface shadow-sm"
    >
      <div className="flex border-b border-border">
        <span className="caption w-24 shrink-0 px-3 py-2 sm:w-32">Cashier</span>
        {DAYS.map((day, i) => (
          <span
            key={day}
            className={cn(
              'caption flex-1 border-l border-border px-3 py-2',
              i >= 2 && 'hidden sm:block',
            )}
          >
            {day}
          </span>
        ))}
      </div>

      {SHIFTS.map((shift) => (
        <div key={shift} className="flex border-b border-border last:border-b-0">
          <span className="w-24 shrink-0 px-3 py-2 text-small text-fg-muted sm:w-32">
            {capitalize(shift)}
          </span>

          {CELLS[shift].map((cell, i) => (
            <div
              key={i}
              className={cn(
                'flex flex-1 flex-col gap-1 border-l border-border px-2 py-2',
                cell.under ? 'bg-coverage-under-bg' : TINT[shift],
                i >= 2 && 'hidden sm:flex',
              )}
            >
              <span className="flex items-center gap-1">
                {cell.under && (
                  <Icon
                    name="warning"
                    size={16}
                    className="shrink-0 text-danger-600"
                  />
                )}
                <span
                  className={cn(
                    'tabular text-caption font-medium',
                    cell.under ? 'text-danger-700' : 'text-fg-muted',
                  )}
                >
                  {cell.count}
                </span>
              </span>

              <span className="flex flex-wrap gap-1">
                {cell.names.map((name) => (
                  <span
                    key={name}
                    className="rounded-sm border border-border bg-surface px-1.5 py-0.5 text-caption text-fg"
                  >
                    {name}
                  </span>
                ))}
              </span>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
