import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import type { Shift } from '@/types'

export type BadgeVariant =
  | 'neutral'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | Shift

const VARIANTS: Record<BadgeVariant, string> = {
  neutral: 'bg-surface-subtle text-fg-muted border-border',
  success: 'bg-success-50 text-success-700 border-success-200',
  warning: 'bg-warning-50 text-warning-700 border-warning-200',
  danger: 'bg-danger-50 text-danger-700 border-danger-200',
  info: 'bg-info-50 text-info-700 border-info-200',
  morning:
    'bg-shift-morning-bg text-shift-morning-fg border-shift-morning-border',
  afternoon:
    'bg-shift-afternoon-bg text-shift-afternoon-fg border-shift-afternoon-border',
  evening:
    'bg-shift-evening-bg text-shift-evening-fg border-shift-evening-border',
}

export interface BadgeProps {
  variant?: BadgeVariant
  children: ReactNode
  className?: string
}

/** Always text — never a bare coloured dot. */
export default function Badge({
  variant = 'neutral',
  children,
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-sm border px-2 py-0.5 text-caption font-medium',
        VARIANTS[variant],
        className,
      )}
    >
      {children}
    </span>
  )
}
