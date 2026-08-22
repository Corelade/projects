import Button from '@/components/button/button'
import Icon from '@/components/icon/icon'

export interface ErrorPanelProps {
  title?: string
  /** The server's actual message — never a generic string. */
  message: string
  onRetry?: () => void
  retrying?: boolean
}

/**
 * Inline, inside the content area. A failed load must never render as a toast
 * alone — the toast vanishes and leaves an empty screen behind.
 */
export default function ErrorPanel({
  title = "That didn't load",
  message,
  onRetry,
  retrying,
}: ErrorPanelProps) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-md border border-danger-200 bg-danger-50 p-4"
    >
      <Icon name="warning" size={20} className="mt-0.5 shrink-0 text-danger-600" />
      <div className="flex-1">
        <p className="text-body font-medium text-fg">{title}</p>
        <p className="mt-0.5 text-small text-fg-muted">{message}</p>
      </div>
      {onRetry && (
        <Button
          size="sm"
          variant="secondary"
          onClick={onRetry}
          loading={retrying}
          iconLeft={<Icon name="refresh" size={16} />}
        >
          Retry
        </Button>
      )}
    </div>
  )
}
