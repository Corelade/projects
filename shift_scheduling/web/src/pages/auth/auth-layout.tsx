import type { ReactNode } from 'react'
import { Link } from 'react-router'

import Logo from '@/components/logo/logo'

export interface AuthLayoutProps {
  title: string
  description?: ReactNode
  children: ReactNode
  /** Sits under the card — the "no account? sign up" line. */
  footer?: ReactNode
}

/**
 * The shell both auth screens share. Deliberately not `layout/`: there's no
 * sidebar or topbar to offer someone who isn't signed in yet.
 */
export default function AuthLayout({
  title,
  description,
  children,
  footer,
}: AuthLayoutProps) {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center bg-surface-subtle px-4 py-10">
      <div className="flex w-full max-w-sm flex-col gap-6">
        <Link
          to="/sign-in"
          className="focus-ring mx-auto flex items-center gap-2.5 rounded-sm text-h2 font-semibold text-fg"
        >
          <Logo size={32} className="text-brand-600" />
          ShiftPro
        </Link>

        <div className="flex flex-col gap-5 rounded-lg border border-border bg-surface p-6">
          <div className="flex flex-col gap-1.5">
            <h1 className="text-h2 font-semibold text-fg">{title}</h1>
            {description && (
              <p className="text-body text-fg-muted">{description}</p>
            )}
          </div>
          {children}
        </div>

        {footer && (
          <p className="text-center text-body text-fg-muted">{footer}</p>
        )}
      </div>
    </main>
  )
}
