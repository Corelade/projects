import { cn } from '@/lib/cn'

export interface AvatarProps {
  initials: string
  size?: 32 | 40
  className?: string
}

export default function Avatar({ initials, size = 32, className }: AvatarProps) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        'inline-flex shrink-0 items-center justify-center rounded-full bg-brand-50 font-medium text-brand-700',
        size === 32 ? 'text-caption' : 'text-small',
        className,
      )}
      style={{ width: size, height: size }}
    >
      {initials}
    </span>
  )
}
