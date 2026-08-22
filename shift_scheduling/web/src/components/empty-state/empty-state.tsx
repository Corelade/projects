import type { ReactNode } from 'react'
import Icon, { type IconName } from '@/components/icon/icon'

export interface EmptyStateProps {
  icon?: IconName
  title: string
  description: string
  /** The action that resolves the emptiness — always ships with one. */
  action?: ReactNode
}

export default function EmptyState({
  icon = 'inbox',
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
      <span className="flex size-12 items-center justify-center rounded-full bg-surface-subtle text-fg-subtle">
        <Icon name={icon} size={24} />
      </span>
      <h3 className="text-h3 font-semibold text-fg">{title}</h3>
      <p className="max-w-80 text-body text-fg-muted">{description}</p>
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
