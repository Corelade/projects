import { useEffect, useState } from 'react'
import Icon from '@/components/icon/icon'

export interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  'aria-label': string
}

/** Debounced 250ms; filters client-side over the loaded collection. */
export default function SearchInput({
  value,
  onChange,
  placeholder = 'Search',
  ...aria
}: SearchInputProps) {
  const [local, setLocal] = useState(value)

  useEffect(() => setLocal(value), [value])

  useEffect(() => {
    if (local === value) return
    const t = setTimeout(() => onChange(local), 250)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [local])

  return (
    <div className="relative w-full max-w-80">
      <Icon
        name="search"
        size={16}
        className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-fg-subtle"
      />
      <input
        {...aria}
        type="search"
        value={local}
        placeholder={placeholder}
        onChange={(e) => setLocal(e.target.value)}
        className="focus-ring h-(--size-control) w-full rounded-md border border-border bg-surface pl-9 pr-9 text-body text-fg placeholder:text-fg-subtle hover:border-border-strong [&::-webkit-search-cancel-button]:hidden"
      />
      {local && (
        <button
          type="button"
          aria-label="Clear search"
          onClick={() => {
            setLocal('')
            onChange('')
          }}
          className="focus-ring absolute right-2 top-1/2 flex size-6 -translate-y-1/2 items-center justify-center rounded-sm text-fg-subtle hover:bg-surface-subtle hover:text-fg"
        >
          <Icon name="x" size={16} />
        </button>
      )}
    </div>
  )
}
