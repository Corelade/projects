import { useState } from 'react'
import Icon from '@/components/icon/icon'
import Input, { type InputProps } from '@/components/input/input'
import { cn } from '@/lib/cn'

/** Input's own props, minus `type` — the reveal state owns that. */
export type PasswordInputProps = Omit<InputProps, 'type'>

/**
 * A drop-in for `<Input type="password">` with a reveal toggle, following the
 * trailing-control recipe `search-input` already uses: a `relative` wrapper,
 * right padding on the input, and the button absolutely placed inside it.
 *
 * The toggle stays in the tab order. It's a real control, and a keyboard user
 * checking what they typed is exactly who needs it.
 */
export default function PasswordInput({
  invalid,
  disabled,
  className,
  ...rest
}: PasswordInputProps) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="relative">
      <Input
        {...rest}
        type={visible ? 'text' : 'password'}
        invalid={invalid}
        disabled={disabled}
        className={cn('pr-9', className)}
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        disabled={disabled}
        /* The label states the action and changes with the state, which is the
           convention. Adding aria-pressed on top double-announces it. */
        aria-label={visible ? 'Hide password' : 'Show password'}
        className="focus-ring absolute right-2 top-1/2 flex size-6 -translate-y-1/2 items-center justify-center rounded-sm text-fg-subtle hover:bg-surface-subtle hover:text-fg disabled:cursor-not-allowed disabled:text-fg-subtle disabled:hover:bg-transparent"
      >
        <Icon name={visible ? 'eye-off' : 'eye'} size={16} />
      </button>
    </div>
  )
}
