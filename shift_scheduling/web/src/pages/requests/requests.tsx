import { useState } from 'react'

import AvailabilityDiff from '@/components/availability-diff/availability-diff'
import Badge, { type BadgeVariant } from '@/components/badge/badge'
import Button from '@/components/button/button'
import EmptyState from '@/components/empty-state/empty-state'
import ErrorPanel from '@/components/error-panel/error-panel'
import Field from '@/components/field/field'
import Input from '@/components/input/input'
import Layout from '@/components/layout/layout'
import Modal from '@/components/modal/modal'
import Skeleton from '@/components/skeleton/skeleton'
import ToggleChipGroup from '@/components/toggle-chip/toggle-chip-group'
import { cn } from '@/lib/cn'
import { formatDateTime } from '@/lib/dates'
import { capitalize } from '@/lib/format'
import { useAppDispatch } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import {
  useApproveRequestMutation,
  useGetAvailabilityRequestsQuery,
  useRejectRequestMutation,
} from '@/store/api/requests-api'
import { pushToast } from '@/store/slices/ui-slice'
import {
  DAYS,
  SHIFTS,
  type AvailabilityRequest,
  type Day,
  type RequestStatus,
  type Shift,
} from '@/types'

const STATUS_BADGE: Record<RequestStatus, BadgeVariant> = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  cancelled: 'neutral',
}

const APPLY_HINT = 'Regenerate the rota to apply it to weeks already generated.'

type Tab = 'pending' | 'history'

/**
 * Staff availability change requests. Pending ones can be approved as asked,
 * adjusted then approved, or rejected with a reason — each notifies the staff
 * member. History lists everything already decided or withdrawn.
 */
export default function RequestsPage() {
  const [tab, setTab] = useState<Tab>('pending')
  const { data, isLoading, isError, error, refetch, isFetching } =
    useGetAvailabilityRequestsQuery()

  const [adjusting, setAdjusting] = useState<AvailabilityRequest | null>(null)
  const [rejecting, setRejecting] = useState<AvailabilityRequest | null>(null)

  const pending = data?.filter((r) => r.status === 'pending') ?? []
  const history = data?.filter((r) => r.status !== 'pending') ?? []
  const visible = tab === 'pending' ? pending : history

  return (
    <Layout
      title="Requests"
      description="Staff asking to change when they can work."
    >
      <div className="flex flex-col gap-4">
        <div role="tablist" aria-label="Requests" className="flex gap-1 border-b border-border">
          {(['pending', 'history'] as const).map((t) => (
            <button
              key={t}
              role="tab"
              type="button"
              aria-selected={tab === t}
              onClick={() => setTab(t)}
              className={cn(
                'focus-ring -mb-px border-b-2 px-3 py-2 text-body',
                tab === t
                  ? 'border-brand-600 font-medium text-brand-700'
                  : 'border-transparent text-fg-muted hover:text-fg',
              )}
            >
              {t === 'pending' ? `Pending${pending.length ? ` (${pending.length})` : ''}` : 'History'}
            </button>
          ))}
        </div>

        {isError ? (
          <ErrorPanel
            title="Couldn't load requests"
            message={errorMessage(error)}
            onRetry={refetch}
            retrying={isFetching}
          />
        ) : isLoading ? (
          <div className="flex flex-col gap-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-lg border border-border bg-surface p-5">
                <Skeleton width="30%" />
                <div className="mt-3">
                  <Skeleton width="60%" />
                </div>
              </div>
            ))}
          </div>
        ) : visible.length === 0 ? (
          <div className="rounded-lg border border-border bg-surface">
            <EmptyState
              icon="inbox"
              title={tab === 'pending' ? 'No pending requests' : 'No past requests'}
              description={
                tab === 'pending'
                  ? 'When staff ask to change their availability, it shows up here.'
                  : 'Approved, rejected and cancelled requests show up here.'
              }
            />
          </div>
        ) : (
          <ul className="flex flex-col gap-3">
            {visible.map((r) => (
              <RequestCard
                key={r.id}
                request={r}
                onAdjust={() => setAdjusting(r)}
                onReject={() => setRejecting(r)}
              />
            ))}
          </ul>
        )}
      </div>

      {adjusting && <AdjustModal request={adjusting} onClose={() => setAdjusting(null)} />}
      {rejecting && <RejectModal request={rejecting} onClose={() => setRejecting(null)} />}
    </Layout>
  )
}

function RequestCard({
  request: r,
  onAdjust,
  onReject,
}: {
  request: AvailabilityRequest
  onAdjust: () => void
  onReject: () => void
}) {
  const dispatch = useAppDispatch()
  const [approve, approveState] = useApproveRequestMutation()

  async function approveAsAsked() {
    try {
      await approve({ id: r.id }).unwrap()
      dispatch(pushToast('success', `Approved ${r.staff_name}'s change. ${APPLY_HINT}`))
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't approve that request.")))
    }
  }

  return (
    <li className="flex flex-col gap-4 rounded-lg border border-border bg-surface p-4 sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-0.5">
          <span className="text-h3 font-semibold text-fg">{r.staff_name}</span>
          <span className="text-small text-fg-muted">
            Requested {formatDateTime(r.created_at)}
            {r.reviewed_at && ` · ${capitalize(r.status)} ${formatDateTime(r.reviewed_at)}`}
          </span>
        </div>
        <Badge variant={STATUS_BADGE[r.status]}>{capitalize(r.status)}</Badge>
      </div>

      {r.note && (
        <p className="rounded-md bg-surface-subtle px-3 py-2 text-body text-fg">
          “{r.note}”
        </p>
      )}

      <AvailabilityDiff
        currentDays={r.current_day_exclusions}
        currentShifts={r.current_shift_exclusions}
        days={r.day_exclusions}
        shifts={r.shift_exclusions}
      />

      {r.admin_note && (
        <p className="text-small text-fg-muted">
          Your note: <span className="text-fg">{r.admin_note}</span>
        </p>
      )}

      {r.status === 'pending' && (
        <div className="flex flex-wrap justify-end gap-2 border-t border-border pt-4">
          <Button variant="ghost" onClick={onReject} disabled={approveState.isLoading}>
            Reject
          </Button>
          <Button onClick={onAdjust} disabled={approveState.isLoading}>
            Adjust &amp; approve
          </Button>
          <Button variant="primary" onClick={approveAsAsked} loading={approveState.isLoading}>
            Approve
          </Button>
        </div>
      )}
    </li>
  )
}

function AdjustModal({
  request,
  onClose,
}: {
  request: AvailabilityRequest
  onClose: () => void
}) {
  const dispatch = useAppDispatch()
  const [approve, { isLoading }] = useApproveRequestMutation()
  const [days, setDays] = useState<Day[]>(request.day_exclusions)
  const [shifts, setShifts] = useState<Shift[]>(request.shift_exclusions)
  const [note, setNote] = useState('')

  const toggle = <T,>(list: T[], v: T) =>
    list.includes(v) ? list.filter((x) => x !== v) : [...list, v]

  async function submit() {
    try {
      await approve({
        id: request.id,
        day_exclusions: days,
        shift_exclusions: shifts,
        admin_note: note.trim() || undefined,
      }).unwrap()
      dispatch(pushToast('success', `Approved ${request.staff_name}'s change. ${APPLY_HINT}`))
      onClose()
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't approve that request.")))
    }
  }

  return (
    <Modal
      title={`Adjust ${request.staff_name}'s request`}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button variant="primary" onClick={submit} loading={isLoading}>
            Approve with changes
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4 pt-1">
        <p>Change what they asked for, then approve. They'll be told it was adjusted.</p>
        <ToggleChipGroup<Day>
          id="adjust_days"
          label="Days not available"
          options={DAYS}
          selected={days}
          onToggle={(d) => setDays((l) => toggle(l, d))}
          renderLabel={(d) => capitalize(d).slice(0, 3)}
          disabled={isLoading}
        />
        <ToggleChipGroup<Shift>
          id="adjust_shifts"
          label="Shifts not available"
          options={SHIFTS}
          selected={shifts}
          onToggle={(s) => setShifts((l) => toggle(l, s))}
          renderLabel={(s) => capitalize(s)}
          disabled={isLoading}
        />
        <Field id="adjust_note" label="Note to them" hint="Optional — why you changed it.">
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

function RejectModal({
  request,
  onClose,
}: {
  request: AvailabilityRequest
  onClose: () => void
}) {
  const dispatch = useAppDispatch()
  const [reject, { isLoading }] = useRejectRequestMutation()
  const [reason, setReason] = useState('')

  async function submit() {
    try {
      await reject({ id: request.id, admin_note: reason.trim() || undefined }).unwrap()
      dispatch(pushToast('success', `Rejected ${request.staff_name}'s request.`))
      onClose()
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't reject that request.")))
    }
  }

  return (
    <Modal
      title={`Reject ${request.staff_name}'s request?`}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button variant="danger" onClick={submit} loading={isLoading}>
            Reject
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4 pt-1">
        <p>Their availability stays as it is. They'll see your reason.</p>
        <Field id="reject_reason" label="Reason" hint="Optional.">
          {(props) => (
            <Input
              {...props}
              autoFocus
              maxLength={500}
              value={reason}
              disabled={isLoading}
              onChange={(e) => setReason(e.target.value)}
            />
          )}
        </Field>
      </div>
    </Modal>
  )
}
