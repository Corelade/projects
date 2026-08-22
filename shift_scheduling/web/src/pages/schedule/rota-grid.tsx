import { Fragment } from 'react'

import Icon from '@/components/icon/icon'
import { cn } from '@/lib/cn'
import { formatDayHeader } from '@/lib/dates'
import { capitalize } from '@/lib/format'
import type { Day, Department, ScheduleCell, Shift } from '@/types'
import { DAYS, SHIFTS } from '@/types'
import { cellKey, coverageOf } from './rota-model'

export interface RotaGridProps {
  weekStart: string
  departments: Department[]
  cells: Map<string, ScheduleCell>
  onSelectCell: (department: Department, day: Day, shift: Shift) => void
}

/**
 * Columns Mon-Sun; rows grouped by department with three shift rows inside.
 * One cell = one (department, shift, day), which is what makes coverage
 * warnings and click-to-edit unambiguous (docs/ui/05-screens.md).
 */
export default function RotaGrid({
  weekStart,
  departments,
  cells,
  onSelectCell,
}: RotaGridProps) {
  return (
    <div className="min-h-0 flex-1 overflow-auto rounded-md border border-border">
      <table className="rota-table" aria-label="Weekly rota">
        <thead>
          <tr>
            <th className="rota-label caption" scope="col">
              Department
            </th>
            {DAYS.map((day) => (
              <th key={day} scope="col" className="caption">
                {formatDayHeader(weekStart, day)}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {departments.map((department) => (
            <Fragment key={department.id}>
              {SHIFTS.map((shift, shiftIndex) => (
                <tr
                  key={`${department.id}-${shift}`}
                  className={cn(shiftIndex === 0 && 'rota-dept-start')}
                >
                  <th scope="row" className="rota-label">
                    {shiftIndex === 0 && (
                      <span className="rota-dept-name block pb-1">
                        {department.name}
                      </span>
                    )}
                    <span className="block text-small font-normal text-fg-muted">
                      {capitalize(shift)}
                    </span>
                  </th>

                  {DAYS.map((day) => {
                    const cell = cells.get(cellKey(department.id, day, shift))
                    const staff = cell?.staff ?? []
                    const coverage = coverageOf(staff.length, department)

                    return (
                      <td key={day}>
                        <button
                          type="button"
                          onClick={() => onSelectCell(department, day, shift)}
                          aria-label={`${department.name}, ${capitalize(shift)}, ${capitalize(day)} — ${staff.length} of ${department.max_staff} assigned`}
                          className={cn(
                            'rota-cell',
                            `rota-cell-${shift}`,
                            coverage === 'under' && 'rota-cell-under',
                            staff.length === 0 && coverage !== 'under' && 'rota-cell-empty',
                          )}
                        >
                          <span className="flex items-center gap-1">
                            {coverage === 'under' && (
                              <Icon
                                name="warning"
                                size={16}
                                className="shrink-0 text-danger-600"
                              />
                            )}
                            {/* Count is text, so the cell survives greyscale. */}
                            <span
                              className={cn(
                                'tabular text-caption font-medium',
                                coverage === 'under'
                                  ? 'rota-under text-danger-700'
                                  : 'text-fg-muted',
                              )}
                            >
                              {staff.length}/{department.max_staff}
                            </span>
                          </span>

                          {staff.length === 0 ? (
                            <span className="text-body text-fg-subtle">—</span>
                          ) : (
                            <span className="flex flex-wrap gap-1">
                              {staff.map((a) => (
                                <span
                                  key={a.staff_id}
                                  className="staff-pill rounded-sm border border-border bg-surface px-1.5 py-0.5 text-caption text-fg"
                                >
                                  {a.staff_name}
                                </span>
                              ))}
                            </span>
                          )}
                        </button>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  )
}
