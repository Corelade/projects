import type { ReactNode } from 'react'
import { useNavigate } from 'react-router'

import Icon from '@/components/icon/icon'
import NotificationBell from '@/components/notification-bell/notification-bell'
import {
  useGetNotificationsQuery,
  useMarkNotificationsReadMutation,
} from '@/store/api/notifications-api'

export interface NavbarProps {
  title: string
  description?: string
  actions?: ReactNode
  /** Opens the slide-over sidebar. Only rendered below `lg`. */
  onOpenNav?: () => void
}

/**
 * One row on desktop. Narrow enough and the actions drop to a second row rather
 * than squeezing the title — a page's controls are worth a line of their own.
 */
export default function Navbar({
  title,
  description,
  actions,
  onOpenNav,
}: NavbarProps) {
  return (
    <header className="no-print flex min-h-(--size-topbar) shrink-0 flex-wrap items-center justify-between gap-x-4 gap-y-3 border-b border-border bg-surface px-4 py-3 sm:px-6 sm:py-2">
      <div className="flex min-w-0 flex-1 items-center gap-2">
        {onOpenNav && (
          <button
            type="button"
            onClick={onOpenNav}
            aria-label="Open menu"
            className="focus-ring -ml-2 flex size-10 shrink-0 items-center justify-center rounded-md text-fg-muted hover:bg-surface-subtle hover:text-fg lg:hidden"
          >
            <Icon name="menu" size={20} />
          </button>
        )}
        <div className="min-w-0">
          <h1 className="truncate text-h2 font-semibold text-fg">{title}</h1>
          {description && (
            <p className="truncate text-small text-fg-muted">{description}</p>
          )}
        </div>
        <div className="ml-auto shrink-0">
          <AdminNotifications />
        </div>
      </div>
      {actions && (
        <div className="flex w-full flex-wrap items-center gap-2 sm:w-auto sm:shrink-0 sm:justify-end">
          {actions}
        </div>
      )}
    </header>
  )
}

/** The admin's bell. Every notification they get is about a request, so each opens /requests. */
function AdminNotifications() {
  const navigate = useNavigate()
  const { data, isLoading } = useGetNotificationsQuery()
  const [markRead] = useMarkNotificationsReadMutation()

  return (
    <NotificationBell
      data={data}
      loading={isLoading}
      onMarkRead={(ids) => markRead(ids)}
      onOpen={(n) => {
        if (n.request_id !== null) navigate('/requests')
      }}
    />
  )
}
