import { useEffect, useRef, type ReactNode } from 'react'

export interface ModalProps {
  title: string
  onClose: () => void
  children: ReactNode
  footer?: ReactNode
  /** Element to focus on open — Cancel, for destructive dialogs. */
  initialFocusRef?: React.RefObject<HTMLElement | null>
}

export default function Modal({
  title,
  onClose,
  children,
  footer,
  initialFocusRef,
}: ModalProps) {
  const panelRef = useRef<HTMLDivElement>(null)
  const returnFocusTo = useRef<HTMLElement | null>(null)

  useEffect(() => {
    returnFocusTo.current = document.activeElement as HTMLElement | null
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    const target =
      initialFocusRef?.current ??
      panelRef.current?.querySelector<HTMLElement>('button, input, [href]')
    target?.focus()

    return () => {
      document.body.style.overflow = previousOverflow
      returnFocusTo.current?.focus()
    }
  }, [initialFocusRef])

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        e.stopPropagation()
        onClose()
        return
      }
      if (e.key !== 'Tab') return

      const focusables = panelRef.current?.querySelectorAll<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
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
    <div
      className="no-print fixed inset-0 flex items-center justify-center p-4"
      style={{ zIndex: 'var(--z-overlay)' }}
    >
      <div
        className="absolute inset-0 bg-slate-900/30"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="relative w-full max-w-120 rounded-lg bg-surface shadow-md"
      >
        <div className="px-5 pb-2 pt-5">
          <h2 id="modal-title" className="text-h3 font-semibold text-fg">
            {title}
          </h2>
        </div>
        <div className="px-5 pb-5 text-body text-fg-muted">{children}</div>
        {footer && (
          <div className="flex justify-end gap-2 border-t border-border px-5 py-4">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
