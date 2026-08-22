import Icon from '@/components/icon/icon'
import { capitalize } from '@/lib/format'
import { SHIFTS } from '@/types'

const SWATCH: Record<string, string> = {
  morning: 'bg-shift-morning-bg border-shift-morning-border',
  afternoon: 'bg-shift-afternoon-bg border-shift-afternoon-border',
  evening: 'bg-shift-evening-bg border-shift-evening-border',
}

/**
 * Printed as well as shown — its whole purpose is to make the grid decodable
 * by someone holding the paper.
 */
export default function ShiftLegend() {
  return (
    <div className="shift-legend flex flex-wrap items-center gap-4 text-small text-fg-muted">
      {SHIFTS.map((shift) => (
        <span key={shift} className="legend-shift inline-flex items-center gap-1.5">
          <span className={`size-3 shrink-0 rounded-sm border ${SWATCH[shift]}`} />
          {capitalize(shift)}
        </span>
      ))}
      <span className="inline-flex items-center gap-1.5 text-danger-700">
        <Icon name="warning" size={16} />
        Below minimum staffing
      </span>
    </div>
  )
}
