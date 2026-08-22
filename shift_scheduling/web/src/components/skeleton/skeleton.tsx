import { cn } from '@/lib/cn'

export interface SkeletonProps {
  variant?: 'text' | 'circle' | 'rect'
  width?: string | number
  height?: string | number
  className?: string
}

/** Skeletons mirror the SHAPE of what's coming — see docs/ui/04-patterns.md. */
export default function Skeleton({
  variant = 'text',
  width,
  height,
  className,
}: SkeletonProps) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        'skeleton block',
        variant === 'circle' && 'rounded-full',
        variant === 'text' && 'rounded-sm',
        variant === 'rect' && 'rounded-md',
        className,
      )}
      style={{
        width: width ?? '100%',
        height: height ?? (variant === 'text' ? '0.875rem' : undefined),
      }}
    />
  )
}
