import { useEffect, useRef, type ReactNode } from 'react'
import Icon from '@/components/icon/icon'
import './drawer.css'

export interface DrawerProps {
  title: string
  subtitle?: string
  onClose: () => void
  footer?: ReactNode
  children: ReactNode
}

/**
 * Focus is trapped inside; Esc closes; focus returns to the trigger on close.
 * A dirty form intercepts onClose to confirm first — that's the caller's job.
 */
export default function Drawer({
  title,
  subtitle,
  onClose,
  footer,
  children,
}: DrawerProps) {
  const panelRef = useRef<HTMLDivElement>(null)
  const returnFocusTo = useRef<HTMLElement | null>(null)

  useEffect(() => {
    returnFocusTo.current = document.activeElement as HTMLElement | null

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    // Focus the first form field, not the header's close button — the drawer
    // exists to be filled in.
    const target =
      panelRef.current?.querySelector<HTMLElement>(
        'input:not([type="hidden"]), select, textarea',
      ) ??
      panelRef.current?.querySelector<HTMLElement>('button, [href]')
    target?.focus()

    return () => {
      document.body.style.overflow = previousOverflow
      returnFocusTo.current?.focus()
    }
  }, [])

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        e.stopPropagation()
        onClose()
        return
      }
      if (e.key !== 'Tab') return

      const focusables = panelRef.current?.querySelectorAll<HTMLElement>(
        'input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
      )
      if (!focusables?.length) return

      const list = Array.from(focusables)
      const first = list[0]
      const last = list[list.length - 1]

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', onKeyDown, true)
    return () => document.removeEventListener('keydown', onKeyDown, true)
  }, [onClose])

  return (
    <>
      <div className="drawer-backdrop no-print" onClick={onClose} />

      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        className="drawer-panel no-print"
      >
        <header className="flex shrink-0 items-start justify-between gap-4 border-b border-border px-5 py-4">
          <div>
            <h2 id="drawer-title" className="text-h3 font-semibold text-fg">
              {title}
            </h2>
            {subtitle && <p className="mt-0.5 text-small text-fg-muted">{subtitle}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="focus-ring flex size-8 shrink-0 items-center justify-center rounded-md text-fg-muted hover:bg-surface-subtle hover:text-fg"
          >
            <Icon name="x" size={20} />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-5 py-5">{children}</div>

        {footer && (
          <footer className="shrink-0 border-t border-border px-5 py-4">
            {footer}
          </footer>
        )}
      </div>
    </>
  )
}
