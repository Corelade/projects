import { useEffect, useRef, useState } from 'react'

import Button from '@/components/button/button'
import Icon from '@/components/icon/icon'
import Spinner from '@/components/spinner/spinner'
import { cn } from '@/lib/cn'
import type { AppNotification, NotificationList } from '@/types'

export interface NotificationBellProps {
  data?: NotificationList
  loading?: boolean
  /** Ids to mark read; no ids marks everything read. */
  onMarkRead: (ids?: number[]) => void
  /** Where a notification leads — called after it's marked read. */
  onOpen?: (notification: AppNotification) => void
}

/**
 * The bell both sides share. It's presentational: the admin navbar and the
 * staff portal each pass their own data and mutations, because the two read
 * from separate endpoints.
 */
export default function NotificationBell({
  data,
  loading,
  onMarkRead,
  onOpen,
}: NotificationBellProps) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const unread = data?.unread ?? 0

  // Outside click and Esc close it.
  useEffect(() => {
    if (!open) return
    function onPointerDown(e: PointerEvent) {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false)
    }
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  function openItem(n: AppNotification) {
    if (!n.read) onMarkRead([n.id])
    setOpen(false)
    onOpen?.(n)
  }

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={unread ? `Notifications, ${unread} unread` : 'Notifications'}
        aria-expanded={open}
        aria-haspopup="true"
        className="focus-ring relative flex size-10 items-center justify-center rounded-md text-fg-muted hover:bg-surface-subtle hover:text-fg"
      >
        <Icon name="bell" size={20} />
        {unread > 0 && (
          <span className="tabular absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-danger-600 px-1 text-[10px] font-semibold leading-none text-fg-inverse">
            {unread > 9 ? '9+' : unread}
          </span>
        )}
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Notifications"
          className="absolute right-0 top-full mt-2 flex max-h-[28rem] w-[min(22rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-lg border border-border bg-surface shadow-md"
          style={{ zIndex: 'var(--z-overlay)' }}
        >
          <div className="flex items-center justify-between gap-2 border-b border-border px-4 py-3">
            <span className="text-body font-semibold text-fg">Notifications</span>
            {unread > 0 && (
              <Button variant="ghost" size="sm" onClick={() => onMarkRead()}>
                Mark all read
              </Button>
            )}
          </div>

          {loading && !data ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : !data?.items.length ? (
            <p className="px-4 py-8 text-center text-body text-fg-muted">
              You're all caught up.
            </p>
          ) : (
            <ul className="min-h-0 flex-1 divide-y divide-border overflow-y-auto">
              {data.items.map((n) => (
                <li key={n.id}>
                  <button
                    type="button"
                    onClick={() => openItem(n)}
                    className={cn(
                      'focus-ring flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-surface-subtle',
                      !n.read && 'bg-brand-50',
                    )}
                  >
                    <span
                      className={cn(
                        'mt-1.5 size-2 shrink-0 rounded-full',
                        n.read ? 'bg-transparent' : 'bg-brand-600',
                      )}
                      aria-hidden="true"
                    />
                    <span className="flex min-w-0 flex-col gap-0.5">
                      <span className={cn('text-body text-fg', !n.read && 'font-medium')}>
                        {n.message}
                      </span>
                      <span className="text-small text-fg-muted">{timeAgo(n.created_at)}</span>
                    </span>
                    {!n.read && <span className="sr-only">(unread)</span>}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

/** "just now", "5 min ago", "3 h ago", then a date. */
function timeAgo(iso: string): string {
  const ms = Date.now() - new Date(iso).getTime()
  const min = Math.round(ms / 60_000)
  if (min < 1) return 'just now'
  if (min < 60) return `${min} min ago`
  const hours = Math.round(min / 60)
  if (hours < 24) return `${hours} h ago`
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}
