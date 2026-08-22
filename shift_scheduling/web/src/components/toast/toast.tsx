import { useEffect } from 'react'
import { cn } from '@/lib/cn'
import Icon, { type IconName } from '@/components/icon/icon'
import { useAppDispatch, useAppSelector } from '@/store'
import { dismissToast, type Toast as ToastData } from '@/store/slices/ui-slice'

const STYLES: Record<ToastData['variant'], string> = {
  success: 'border-success-200 bg-success-50 text-success-700',
  error: 'border-danger-200 bg-danger-50 text-danger-700',
  info: 'border-info-200 bg-info-50 text-info-700',
}

const ICONS: Record<ToastData['variant'], IconName> = {
  success: 'check-circle',
  error: 'x-circle',
  info: 'info',
}

function ToastItem({ toast }: { toast: ToastData }) {
  const dispatch = useAppDispatch()

  useEffect(() => {
    // Errors persist until dismissed; the rest auto-dismiss after 5s.
    if (toast.variant === 'error') return
    const t = setTimeout(() => dispatch(dismissToast(toast.id)), 5000)
    return () => clearTimeout(t)
  }, [dispatch, toast.id, toast.variant])

  return (
    <div
      className={cn(
        'pointer-events-auto flex w-90 items-start gap-2.5 rounded-md border p-3 shadow-sm',
        STYLES[toast.variant],
      )}
    >
      <Icon name={ICONS[toast.variant]} size={20} className="mt-px shrink-0" />
      <p className="flex-1 text-small text-fg">{toast.message}</p>
      <button
        type="button"
        aria-label="Dismiss"
        onClick={() => dispatch(dismissToast(toast.id))}
        className="focus-ring flex size-5 shrink-0 items-center justify-center rounded-sm text-fg-muted hover:text-fg"
      >
        <Icon name="x" size={16} />
      </button>
    </div>
  )
}

export default function ToastStack() {
  const toasts = useAppSelector((s) => s.ui.toasts)

  return (
    <div
      role="status"
      aria-live="polite"
      className="no-print pointer-events-none fixed bottom-6 right-6 flex flex-col gap-2"
      style={{ zIndex: 'var(--z-toast)' }}
    >
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  )
}
