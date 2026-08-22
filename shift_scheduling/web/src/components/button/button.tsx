import type { ButtonHTMLAttributes, ReactNode, Ref } from 'react'
import { cn } from '@/lib/cn'
import Spinner from '@/components/spinner/spinner'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'
export type ButtonSize = 'sm' | 'md'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  iconLeft?: ReactNode
  iconRight?: ReactNode
  fullWidth?: boolean
  /** React 19 passes ref as a normal prop to function components. */
  ref?: Ref<HTMLButtonElement>
}

const VARIANTS: Record<ButtonVariant, string> = {
  primary:
    'bg-brand-600 text-fg-inverse hover:bg-brand-700 active:bg-brand-800 border border-transparent',
  secondary:
    'bg-surface text-fg border border-border hover:bg-surface-subtle hover:border-border-strong active:bg-slate-200',
  ghost:
    'bg-transparent text-fg-muted border border-transparent hover:bg-surface-subtle hover:text-fg active:bg-slate-200',
  danger:
    'bg-danger-600 text-fg-inverse hover:bg-danger-700 active:bg-danger-700 border border-transparent',
}

const SIZES: Record<ButtonSize, string> = {
  sm: 'h-(--size-control-sm) px-3 text-small gap-1.5',
  md: 'h-(--size-control) px-4 text-body gap-2',
}

export default function Button({
  variant = 'secondary',
  size = 'md',
  loading = false,
  iconLeft,
  iconRight,
  fullWidth,
  disabled,
  children,
  className,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || loading

  return (
    <button
      {...rest}
      disabled={isDisabled}
      aria-busy={loading || undefined}
      className={cn(
        'focus-ring inline-flex items-center justify-center rounded-md font-medium',
        'transition-colors duration-(--duration-fast)',
        SIZES[size],
        VARIANTS[variant],
        fullWidth ? 'w-full min-w-0' : 'shrink-0',
        // Disabled must read as LESS prominent than enabled.
        isDisabled &&
          'cursor-not-allowed border-border bg-surface-subtle text-fg-subtle hover:bg-surface-subtle hover:text-fg-subtle',
        className,
      )}
    >
      {/* Reserve the icon slot so width doesn't change when loading starts. */}
      {(iconLeft || loading) && (
        <span className="inline-flex shrink-0 items-center">
          {loading ? <Spinner size={16} /> : iconLeft}
        </span>
      )}
      {children}
      {iconRight && !loading && (
        <span className="inline-flex shrink-0 items-center">{iconRight}</span>
      )}
    </button>
  )
}
