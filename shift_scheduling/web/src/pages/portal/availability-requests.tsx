import { useState } from 'react'

import AvailabilityDiff from '@/components/availability-diff/availability-diff'
import Badge from '@/components/badge/badge'
import Button from '@/components/button/button'
import Field from '@/components/field/field'
import Input from '@/components/input/input'
import Modal from '@/components/modal/modal'
import ToggleChipGroup from '@/components/toggle-chip/toggle-chip-group'
import { formatDateTime } from '@/lib/dates'
import { capitalize } from '@/lib/format'
import { availableHours } from '@/lib/validation'
import { useAppDispatch } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import {
  useCancelRequestMutation,
  useGetMyRequestsQuery,
  useRequestAvailabilityChangeMutation,
} from '@/store/api/requests-api'
import { pushToast } from '@/store/slices/ui-slice'
import { DAYS, SHIFTS, type Day, type PortalProfile, type Shift } from '@/types'

/**
 * The staff member's side of availability requests, under My availability:
 * a button to ask for a change, the pending request (cancellable), and the
 * manager's latest decision with their note.
 */
export default function AvailabilityRequests({ profile }: { profile: PortalProfile }) {
  const dispatch = useAppDispatch()
  const { data } = useGetMyRequestsQuery()
  const [cancel, cancelState] = useCancelRequestMutation()
  const [open, setOpen] = useState(false)

  const pending = data?.find((r) => r.status === 'pending')
  const latest = data?.find((r) => r.status === 'approved' || r.status === 'rejected')

  async function cancelPending() {
    if (!pending) return
    try {
      await cancel(pending.id).unwrap()
      dispatch(pushToast('success', 'Request cancelled.'))
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't cancel the request.")))
    }
  }

  return (
    <div className="flex flex-col gap-3 border-t border-border pt-4">
      {pending ? (
        <div className="flex flex-col gap-3 rounded-md border border-warning-200 bg-warning-50 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-body font-medium text-fg">
              Change requested {formatDateTime(pending.created_at)} · waiting for your manager
            </span>
            <div className="flex gap-2">
              <Button size="sm" onClick={() => setOpen(true)} disabled={cancelState.isLoading}>
                Edit request
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={cancelPending}
                loading={cancelState.isLoading}
              >
                Cancel request
              </Button>
            </div>
          </div>
          <AvailabilityDiff
            currentDays={pending.current_day_exclusions}
            currentShifts={pending.current_shift_exclusions}
            days={pending.day_exclusions}
            shifts={pending.shift_exclusions}
          />
        </div>
      ) : (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-body text-fg-muted">Need different days or shifts?</p>
          <Button variant="primary" onClick={() => setOpen(true)}>
            Request a change
          </Button>
        </div>
      )}

      {latest && (
        <p className="text-small text-fg-muted">
          <Badge variant={latest.status === 'approved' ? 'success' : 'danger'}>
            {capitalize(latest.status)}
          </Badge>{' '}
          Your last request ({formatDateTime(latest.created_at)})
          {latest.admin_note && (
            <>
              {' '}— <span className="text-fg">“{latest.admin_note}”</span>
            </>
          )}
        </p>
      )}

      {open && (
        <RequestChangeModal
          profile={profile}
          initialDays={pending?.day_exclusions ?? profile.day_exclusions}
          initialShifts={pending?.shift_exclusions ?? profile.shift_exclusions}
          initialNote={pending?.note ?? ''}
          replacing={Boolean(pending)}
          onClose={() => setOpen(false)}
        />
      )}
    </div>
  )
}

function RequestChangeModal({
  profile,
  initialDays,
  initialShifts,
  initialNote,
  replacing,
  onClose,
}: {
  profile: PortalProfile
  initialDays: Day[]
  initialShifts: Shift[]
  initialNote: string
  replacing: boolean
  onClose: () => void
}) {
  const dispatch = useAppDispatch()
  const [submit, { isLoading }] = useRequestAvailabilityChangeMutation()
  const [days, setDays] = useState<Day[]>(initialDays)
  const [shifts, setShifts] = useState<Shift[]>(initialShifts)
  const [note, setNote] = useState(initialNote)

  const toggle = <T,>(list: T[], v: T) =>
    list.includes(v) ? list.filter((x) => x !== v) : [...list, v]

  // Same rule the server enforces (classes.py StaffData._is_feasible).
  const hours = availableHours(days, shifts)
  const tooFew = hours < profile.contract_hours
  const unchanged =
    sameSet(days, profile.day_exclusions) && sameSet(shifts, profile.shift_exclusions)

  async function send() {
    try {
      await submit({
        day_exclusions: days,
        shift_exclusions: shifts,
        note: note.trim() || undefined,
      }).unwrap()
      dispatch(
        pushToast(
          'success',
          replacing ? 'Request updated.' : 'Request sent. Your manager will review it.',
        ),
      )
      onClose()
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't send the request.")))
    }
  }

  return (
    <Modal
      title={replacing ? 'Edit your request' : 'Request an availability change'}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={send}
            loading={isLoading}
            disabled={tooFew || unchanged}
          >
            {replacing ? 'Update request' : 'Send request'}
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4 pt-1">
        <p>Choose when you <span className="font-medium text-fg">can't</span> work. Your manager reviews it before anything changes.</p>
        <ToggleChipGroup<Day>
          id="request_days"
          label="Days not available"
          options={DAYS}
          selected={days}
          onToggle={(d) => setDays((l) => toggle(l, d))}
          renderLabel={(d) => capitalize(d).slice(0, 3)}
          disabled={isLoading}
        />
        <ToggleChipGroup<Shift>
          id="request_shifts"
          label="Shifts not available"
          options={SHIFTS}
          selected={shifts}
          onToggle={(s) => setShifts((l) => toggle(l, s))}
          renderLabel={(s) => capitalize(s)}
          disabled={isLoading}
          error={
            tooFew
              ? `That leaves ${hours} h a week you could work — less than your ${profile.contract_hours} h contract.`
              : undefined
          }
          hint={unchanged ? "That's your current availability — change something to send a request." : undefined}
        />
        <Field id="request_note" label="Note for your manager" hint="Optional — e.g. why, or from when.">
          {(props) => (
            <Input
              {...props}
              maxLength={500}
              value={note}
              disabled={isLoading}
              onChange={(e) => setNote(e.target.value)}
            />
          )}
        </Field>
      </div>
    </Modal>
  )
}

function sameSet(a: string[], b: string[]) {
  return a.length === b.length && a.every((x) => b.includes(x))
}
