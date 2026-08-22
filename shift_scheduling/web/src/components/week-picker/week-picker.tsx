import Button from '@/components/button/button'
import Icon from '@/components/icon/icon'
import { addWeeks, currentWeekStart, formatWeekRange, isCurrentWeek } from '@/lib/dates'

export interface WeekPickerProps {
  weekStart: string
  onChange: (weekStart: string) => void
  disabled?: boolean
}

/** Weeks run Monday->Sunday to match DAY_OF_WEEK in app.py. */
export default function WeekPicker({
  weekStart,
  onChange,
  disabled,
}: WeekPickerProps) {
  const atCurrent = isCurrentWeek(weekStart)

  return (
    <div
      className="flex items-center gap-1"
      onKeyDown={(e) => {
        if (disabled) return
        if (e.key === 'ArrowLeft') onChange(addWeeks(weekStart, -1))
        if (e.key === 'ArrowRight') onChange(addWeeks(weekStart, 1))
      }}
    >
      <Button
        variant="ghost"
        size="sm"
        aria-label="Previous week"
        disabled={disabled}
        onClick={() => onChange(addWeeks(weekStart, -1))}
      >
        <Icon name="chevron-left" size={16} />
      </Button>

      <span className="tabular min-w-44 text-center text-body font-medium text-fg">
        {formatWeekRange(weekStart)}
      </span>

      <Button
        variant="ghost"
        size="sm"
        aria-label="Next week"
        disabled={disabled}
        onClick={() => onChange(addWeeks(weekStart, 1))}
      >
        <Icon name="chevron-right" size={16} />
      </Button>

      <Button
        variant="secondary"
        size="sm"
        disabled={disabled || atCurrent}
        onClick={() => onChange(currentWeekStart())}
        className="ml-1"
      >
        This week
      </Button>
    </div>
  )
}
