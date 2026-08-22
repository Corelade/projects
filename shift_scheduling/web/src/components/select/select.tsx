import type { SelectHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'
import Icon from '@/components/icon/icon'

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  invalid?: boolean
}

/**
 * Native <select> deliberately: keyboard behaviour and mobile pickers come
 * free, and nothing here needs custom option rendering.
 */
export default function Select({ invalid, className, children, ...rest }: SelectProps) {
  return (
    <div className="relative">
      <select
        {...rest}
        className={cn(
          'focus-ring h-(--size-control) w-full appearance-none rounded-md border bg-surface pl-3 pr-9 text-body text-fg',
          'transition-colors duration-(--duration-fast)',
          invalid
            ? 'border-danger-600 hover:border-danger-700'
            : 'border-border hover:border-border-strong',
          'disabled:cursor-not-allowed disabled:bg-surface-subtle disabled:text-fg-subtle',
          className,
        )}
      >
        {children}
      </select>
      <Icon
        name="chevron-up-down"
        size={16}
        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-fg-subtle"
      />
    </div>
  )
}
