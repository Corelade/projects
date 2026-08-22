import type { ReactNode } from 'react'

export interface NavbarProps {
  title: string
  description?: string
  actions?: ReactNode
}

export default function Navbar({ title, description, actions }: NavbarProps) {
  return (
    <header className="no-print flex min-h-(--size-topbar) shrink-0 items-center justify-between gap-4 border-b border-border bg-surface px-6">
      <div>
        <h1 className="text-h2 font-semibold text-fg">{title}</h1>
        {description && (
          <p className="text-small text-fg-muted">{description}</p>
        )}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </header>
  )
}
