import type { InputHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean
}

export default function Input({ invalid, className, ...rest }: InputProps) {
  return (
    <input
      {...rest}
      className={cn(
        'focus-ring h-(--size-control) w-full rounded-md border bg-surface px-3 text-body text-fg',
        'placeholder:text-fg-subtle',
        'transition-colors duration-(--duration-fast)',
        invalid
          ? 'border-danger-600 hover:border-danger-700'
          : 'border-border hover:border-border-strong',
        'disabled:cursor-not-allowed disabled:bg-surface-subtle disabled:text-fg-subtle',
        className,
      )}
    />
  )
}
