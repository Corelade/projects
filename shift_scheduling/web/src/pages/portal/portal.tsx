import { useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router'

import Avatar from '@/components/avatar/avatar'
import Badge from '@/components/badge/badge'
import Button from '@/components/button/button'
import EmptyState from '@/components/empty-state/empty-state'
import ErrorPanel from '@/components/error-panel/error-panel'
import Icon from '@/components/icon/icon'
import Logo from '@/components/logo/logo'
import Select from '@/components/select/select'
import Skeleton from '@/components/skeleton/skeleton'
import WeekPicker from '@/components/week-picker/week-picker'
import { cn } from '@/lib/cn'
import { currentWeekStart, dateOfDay, toISODate } from '@/lib/dates'
import { capitalize, fullName, initials } from '@/lib/format'
import { useAppDispatch, useAppSelector } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import { useGetPortalProfileQuery, useGetPortalWeekQuery } from '@/store/api/portal-api'
import { useGetStaffQuery } from '@/store/api/staff-api'
import {
  useGetPortalNotificationsQuery,
  useMarkPortalNotificationsReadMutation,
} from '@/store/api/notifications-api'
import NotificationBell from '@/components/notification-bell/notification-bell'
import AvailabilityRequests from './availability-requests'
import { signedOut } from '@/store/slices/auth-slice'
import {
  DAYS,
  HOURS_PER_SHIFT,
  POSITION_LABELS,
  SHIFTS,
  type PortalProfile,
  type PortalShift,
} from '@/types'

/**
 * The staff-facing page: this person's shifts for a week, and when they're
 * available to work.
 *
 * Staff only ever see themselves. An admin gets the same page plus a picker
 * over their roster — ?staff=<id> — so they can see exactly what someone sees.
 * The week is linkable too: ?week=2026-09-14.
 */
export default function PortalPage() {
  const session = useAppSelector((s) => s.auth.session)
  const isAdmin = session?.user.role === 'admin'
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  const weekStart = searchParams.get('week') ?? currentWeekStart()
  const staffParam = searchParams.get('staff')

  // Admins need a roster to pick from; staff can't load it (and don't need to).
  const roster = useGetStaffQuery(undefined, { skip: !isAdmin })
  const staffId = isAdmin
    ? staffParam
      ? Number(staffParam)
      : roster.data?.[0]?.id
    : undefined

  // Pin the admin's default pick into the URL so it survives a reload.
  useEffect(() => {
    if (isAdmin && !staffParam && staffId !== undefined) {
      setParam('staff', String(staffId), true)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin, staffParam, staffId])

  const waitingForPick = isAdmin && staffId === undefined
  const profile = useGetPortalProfileQuery(staffId, { skip: waitingForPick })
  const week = useGetPortalWeekQuery({ weekStart, staffId }, { skip: waitingForPick })

  function setParam(key: string, value: string, replace = false) {
    const next = new URLSearchParams(searchParams)
    next.set(key, value)
    setSearchParams(next, { replace })
  }

  return (
    <div className="flex min-h-dvh flex-col bg-surface-subtle">
      <PortalHeader
        isAdmin={isAdmin}
        name={session?.user.username ?? ''}
        picker={
          isAdmin && roster.data?.length ? (
            <Select
              aria-label="Viewing staff member"
              value={staffId ?? ''}
              onChange={(e) => setParam('staff', e.target.value)}
              className="min-w-52"
            >
              {roster.data.map((s) => (
                <option key={s.id} value={s.id}>
                  {fullName(s)}
                </option>
              ))}
            </Select>
          ) : null
        }
      />

      <main className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-6 sm:px-6">
        {isAdmin && roster.isSuccess && roster.data.length === 0 ? (
          <Card>
            <EmptyState
              icon="users"
              title="No staff yet"
              description="Add staff to your roster, then come back to see their page."
              action={
                <Button variant="primary" onClick={() => navigate('/staff/new')}>
                  Add staff
                </Button>
              }
            />
          </Card>
        ) : profile.isError ? (
          <ErrorPanel
            title="Couldn't load this page"
            message={errorMessage(profile.error)}
            onRetry={profile.refetch}
            retrying={profile.isFetching}
          />
        ) : (
          <>
            <ProfileCard profile={profile.data} isAdmin={isAdmin} />

            <Card
              title="My schedule"
              actions={
                <WeekPicker
                  weekStart={weekStart}
                  onChange={(next) => setParam('week', next)}
                  disabled={week.isFetching && !week.data}
                />
              }
            >
              {week.isError ? (
                <ErrorPanel
                  title="Couldn't load the schedule"
                  message={errorMessage(week.error)}
                  onRetry={week.refetch}
                  retrying={week.isFetching}
                />
              ) : !week.data || !profile.data ? (
                <WeekSkeleton />
              ) : (
                <WeekSchedule
                  weekStart={week.data.week_start}
                  published={week.data.published}
                  shifts={week.data.shifts}
                  hours={week.data.hours}
                  contractHours={profile.data.contract_hours}
                />
              )}
            </Card>

            <Card title="My availability" id="availability">
              {profile.data ? (
                <>
                  <Availability profile={profile.data} isAdmin={isAdmin} />
                  {/* Requests are the staff member's own; admins edit on the Staff page. */}
                  {!isAdmin && <AvailabilityRequests profile={profile.data} />}
                </>
              ) : (
                <WeekSkeleton />
              )}
            </Card>
          </>
        )}
      </main>
    </div>
  )
}

function PortalHeader({
  isAdmin,
  name,
  picker,
}: {
  isAdmin: boolean
  name: string
  picker: React.ReactNode
}) {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  /** A full reload, for the same reasons as the sidebar's sign-out. */
  function signOut() {
    dispatch(signedOut())
    window.location.assign(`${import.meta.env.BASE_URL}portal/sign-in`)
  }

  return (
    <header className="flex min-h-(--size-topbar) flex-wrap items-center justify-between gap-3 border-b border-border bg-surface px-4 py-3 sm:px-6">
      <div className="flex items-center gap-2.5 text-h3 font-semibold text-fg">
        <Logo size={24} className="shrink-0 text-brand-600" />
        ShiftPro
        <Badge variant="info">{isAdmin ? 'Staff view' : 'Staff'}</Badge>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {picker}
        {isAdmin ? (
          <Button
            variant="ghost"
            size="sm"
            iconLeft={<Icon name="chevron-left" size={16} />}
            onClick={() => navigate('/schedule')}
          >
            Back to admin
          </Button>
        ) : (
          <>
            <span className="hidden text-body text-fg-muted sm:inline">{name}</span>
            <StaffNotifications />
          </>
        )}
        <Button
          variant="ghost"
          size="sm"
          iconLeft={<Icon name="logout" size={16} />}
          onClick={signOut}
        >
          Sign out
        </Button>
      </div>
    </header>
  )
}

/** Every staff notification is about their availability, so each one scrolls there. */
function StaffNotifications() {
  const { data, isLoading } = useGetPortalNotificationsQuery()
  const [markRead] = useMarkPortalNotificationsReadMutation()

  return (
    <NotificationBell
      data={data}
      loading={isLoading}
      onMarkRead={(ids) => markRead(ids)}
      onOpen={() =>
        document.getElementById('availability')?.scrollIntoView({ behavior: 'smooth' })
      }
    />
  )
}

function Card({
  title,
  actions,
  children,
  id,
}: {
  title?: string
  actions?: React.ReactNode
  children: React.ReactNode
  id?: string
}) {
  return (
    <section
      id={id}
      className="flex scroll-mt-4 flex-col gap-4 rounded-lg border border-border bg-surface p-4 sm:p-5"
    >
      {(title || actions) && (
        <div className="flex flex-wrap items-center justify-between gap-3">
          {title && <h2 className="text-h3 font-semibold text-fg">{title}</h2>}
          {actions}
        </div>
      )}
      {children}
    </section>
  )
}

function ProfileCard({
  profile,
  isAdmin,
}: {
  profile?: PortalProfile
  isAdmin: boolean
}) {
  if (!profile) {
    return (
      <Card>
        <div className="flex items-center gap-3">
          <Skeleton variant="circle" width={40} height={40} />
          <Skeleton width="30%" />
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Avatar initials={initials(profile)} size={40} />
          <div className="flex flex-col">
            <span className="text-h3 font-semibold text-fg">{fullName(profile)}</span>
            <span className="text-small text-fg-muted">{profile.email}</span>
          </div>
          <Badge>{POSITION_LABELS[profile.position] ?? capitalize(profile.position)}</Badge>
          {isAdmin && !profile.has_account && (
            <Badge variant="warning">No password yet</Badge>
          )}
        </div>

        <dl className="flex gap-6">
          <Stat label="Contract" value={`${profile.contract_hours} h / week`} />
          <Stat label="Minimum" value={`${profile.min_hours} h / week`} />
        </dl>
      </div>
    </Card>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col">
      <dt className="text-caption text-fg-muted">{label}</dt>
      <dd className="tabular text-body font-medium text-fg">{value}</dd>
    </div>
  )
}

function WeekSchedule({
  weekStart,
  published,
  shifts,
  hours,
  contractHours,
}: {
  weekStart: string
  published: boolean
  shifts: PortalShift[]
  hours: number
  contractHours: number
}) {
  const today = toISODate(new Date())
  const byDay = useMemo(() => {
    const map = new Map<string, PortalShift[]>()
    for (const s of shifts) map.set(s.day, [...(map.get(s.day) ?? []), s])
    return map
  }, [shifts])

  if (!published) {
    return (
      <EmptyState
        icon="calendar"
        title="No rota for this week yet"
        description="Your shifts will show here once your manager publishes this week's rota."
      />
    )
  }

  return (
    <div className="flex flex-col gap-3">
      <p className="text-body text-fg-muted">
        <span className="tabular font-medium text-fg">{hours} h</span> scheduled of{' '}
        {contractHours} h contract · {shifts.length}{' '}
        {shifts.length === 1 ? 'shift' : 'shifts'} of {HOURS_PER_SHIFT} h
      </p>

      <ul className="flex flex-col divide-y divide-border overflow-hidden rounded-md border border-border">
        {DAYS.map((day) => {
          const date = dateOfDay(weekStart, day)
          const isToday = toISODate(date) === today
          const dayShifts = byDay.get(day) ?? []

          return (
            <li
              key={day}
              className={cn(
                'flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3',
                isToday && 'bg-brand-50',
              )}
            >
              <div className="flex w-32 shrink-0 flex-col">
                <span className="text-body font-medium text-fg">
                  {capitalize(day)}
                  {isToday && (
                    <span className="ml-2 text-caption font-medium text-brand-700">Today</span>
                  )}
                </span>
                <span className="text-small text-fg-muted">
                  {date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                </span>
              </div>

              {dayShifts.length ? (
                <div className="flex flex-wrap gap-2">
                  {dayShifts.map((s) => (
                    <Badge key={`${s.shift}-${s.department_id}`} variant={s.shift}>
                      {capitalize(s.shift)} · {capitalize(s.department_name)}
                    </Badge>
                  ))}
                </div>
              ) : (
                <span className="text-body text-fg-subtle">Off</span>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}

/** Day × shift grid: what the scheduler may give them, and what it won't. */
function Availability({ profile, isAdmin }: { profile: PortalProfile; isAdmin: boolean }) {
  const offDays = new Set(profile.day_exclusions)
  const offShifts = new Set(profile.shift_exclusions)

  return (
    <div className="flex flex-col gap-3">
      <p className="text-body text-fg-muted">
        {offDays.size === 0 && offShifts.size === 0
          ? 'You can be scheduled on any day and any shift.'
          : 'The scheduler never gives you a shift you’re marked unavailable for.'}{' '}
        {isAdmin
          ? 'Staff can request changes here; you can edit it on the Staff page.'
          : 'Request a change below and your manager will review it.'}
      </p>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[560px] border-collapse text-small">
          <thead>
            <tr>
              <th className="w-28 py-2 text-left font-medium text-fg-muted">
                <span className="sr-only">Shift</span>
              </th>
              {DAYS.map((day) => (
                <th key={day} className="py-2 text-center font-medium text-fg-muted">
                  {capitalize(day).slice(0, 3)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {SHIFTS.map((shift) => (
              <tr key={shift} className="border-t border-border">
                <th scope="row" className="py-2 text-left font-medium text-fg">
                  {capitalize(shift)}
                </th>
                {DAYS.map((day) => {
                  const available = !offDays.has(day) && !offShifts.has(shift)
                  return (
                    <td key={day} className="p-1 text-center">
                      <span
                        className={cn(
                          'inline-flex h-8 w-full items-center justify-center rounded-sm border',
                          available
                            ? 'border-success-200 bg-success-50 text-success-700'
                            : 'border-border bg-surface-subtle text-fg-subtle',
                        )}
                        title={`${capitalize(day)} ${shift}: ${available ? 'available' : 'unavailable'}`}
                      >
                        <Icon name={available ? 'check' : 'minus'} size={16} />
                        <span className="sr-only">
                          {available ? 'Available' : 'Unavailable'}
                        </span>
                      </span>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function WeekSkeleton() {
  return (
    <div className="flex flex-col gap-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <Skeleton key={i} width="100%" />
      ))}
    </div>
  )
}
