import { cn } from '@/lib/cn'

export interface SpinnerProps {
  size?: 16 | 20 | 32
  className?: string
  label?: string
}

export default function Spinner({ size = 20, className, label }: SpinnerProps) {
  return (
    <span
      className={cn('spinner inline-block animate-spin rounded-full', className)}
      style={{
        width: size,
        height: size,
        borderWidth: size >= 32 ? 3 : 2,
        borderStyle: 'solid',
        borderColor: 'currentColor',
        borderTopColor: 'transparent',
      }}
      role={label ? 'status' : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
    />
  )
}
