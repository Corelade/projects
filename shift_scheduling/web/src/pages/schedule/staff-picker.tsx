import { useMemo, useState } from 'react'

import Button from '@/components/button/button'
import Icon from '@/components/icon/icon'
import Modal from '@/components/modal/modal'
import SearchInput from '@/components/search-input/search-input'
import { cn } from '@/lib/cn'
import { capitalize, fullName, initials } from '@/lib/format'
import Avatar from '@/components/avatar/avatar'
import type { Day, Department, Shift, Staff } from '@/types'
import { availabilityFor } from './rota-model'

export interface StaffPickerProps {
  department: Department
  day: Day
  shift: Shift
  allStaff: Staff[]
  assignedIds: number[]
  hours: Map<number, number>
  dayDepartment: Map<string, number>
  saving: boolean
  onSave: (staffIds: number[]) => void
  onClose: () => void
}

export default function StaffPicker({
  department,
  day,
  shift,
  allStaff,
  assignedIds,
  hours,
  dayDepartment,
  saving,
  onSave,
  onClose,
}: StaffPickerProps) {
  const [selected, setSelected] = useState<number[]>(assignedIds)
  const [search, setSearch] = useState('')

  const rows = useMemo(() => {
    const q = search.trim().toLowerCase()
    return allStaff
      .filter((s) => (q ? fullName(s).toLowerCase().includes(q) : true))
      .map((s) => ({
        staff: s,
        availability: availabilityFor(s, {
          day,
          shift,
          departmentId: department.id,
          hours,
          dayDepartment,
          alreadyInCell: assignedIds.includes(s.id),
        }),
      }))
      .sort((a, b) => {
        // Who's already in this cell first — that's the question the manager
        // opened the picker to answer. Then available, then blocked.
        const aAssigned = assignedIds.includes(a.staff.id)
        const bAssigned = assignedIds.includes(b.staff.id)
        if (aAssigned !== bAssigned) return aAssigned ? -1 : 1
        if (a.availability.available !== b.availability.available) {
          return a.availability.available ? -1 : 1
        }
        return fullName(a.staff).localeCompare(fullName(b.staff))
      })
  }, [allStaff, search, day, shift, department.id, hours, dayDepartment, assignedIds])

  const atCapacity = selected.length >= department.max_staff

  function toggle(id: number) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    )
  }

  return (
    <Modal
      title={`${department.name} · ${capitalize(shift)}`}
      onClose={saving ? () => {} : onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button variant="primary" loading={saving} onClick={() => onSave(selected)}>
            Save cell
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-3">
        <p className="text-small text-fg-muted">
          {capitalize(day)} · {selected.length} of {department.max_staff} assigned
          {selected.length < department.min_staff && (
            <span className="text-danger-700">
              {' '}
              · needs at least {department.min_staff}
            </span>
          )}
        </p>

        <SearchInput
          aria-label="Search staff to assign"
          placeholder="Search staff"
          value={search}
          onChange={setSearch}
        />

        <ul className="-mx-1 max-h-80 overflow-y-auto">
          {rows.map(({ staff, availability }) => {
            const checked = selected.includes(staff.id)
            const blocked = !availability.available || (atCapacity && !checked)
            const reason = !availability.available
              ? availability.reason
              : atCapacity && !checked
                ? `${department.name} takes at most ${department.max_staff}`
                : undefined

            return (
              <li key={staff.id}>
                <label
                  className={cn(
                    'flex cursor-pointer items-center gap-2.5 rounded-md px-1 py-2',
                    blocked ? 'cursor-not-allowed opacity-55' : 'hover:bg-surface-subtle',
                  )}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    disabled={blocked || saving}
                    onChange={() => toggle(staff.id)}
                    className="focus-ring size-4 shrink-0 accent-brand-600"
                  />
                  <Avatar initials={initials(staff)} />
                  <span className="flex min-w-0 flex-1 flex-col">
                    <span className="truncate text-body text-fg">{fullName(staff)}</span>
                    {reason && (
                      <span className="truncate text-small text-fg-muted">{reason}</span>
                    )}
                  </span>
                  <span className="tabular shrink-0 text-small text-fg-muted">
                    {hours.get(staff.id) ?? 0}/{staff.contract_hours} h
                  </span>
                </label>
              </li>
            )
          })}

          {rows.length === 0 && (
            <li className="flex items-center gap-2 px-1 py-6 text-small text-fg-muted">
              <Icon name="search" size={16} />
              No staff match “{search}”.
            </li>
          )}
        </ul>
      </div>
    </Modal>
  )
}
