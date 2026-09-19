import type { ReactNode } from 'react'
import { Navigate, useLocation, useSearchParams } from 'react-router'

import { useAppSelector } from '@/store'
import type { Role } from '@/store/api/auth-api'

/**
 * Gate for everything behind sign-in.
 *
 * `hydrated` is what stops the flash: on a reload the stored session is read
 * back synchronously in store/index.ts, but rendering `null` until the flag is
 * set keeps this correct if that ever becomes async. Redirecting on a session
 * we haven't looked for yet would bounce a signed-in user to the sign-in page
 * on every refresh.
 */
export default function RequireAuth({ children }: { children: ReactNode }) {
  const { session, hydrated } = useAppSelector((s) => s.auth)
  const location = useLocation()

  if (!hydrated) return null

  if (!session) {
    // Carry where they were headed so sign-in can hand them back to it,
    // search string included — /staff?q=ada should survive the round trip.
    const from = `${location.pathname}${location.search}`
    return <Navigate to={`/sign-in?from=${encodeURIComponent(from)}`} replace />
  }

  // The admin app is admin-only. A staff token would 401 on every request
  // here anyway (and sign them out); send them to their own page instead.
  if (session.user.role === 'staff') return <Navigate to="/portal" replace />

  return <>{children}</>
}

/**
 * The staff portal's gate. Any session gets in — staff see themselves, admins
 * pick one of their staff — and no session goes to the portal's own sign-in.
 */
export function RequirePortal({ children }: { children: ReactNode }) {
  const { session, hydrated } = useAppSelector((s) => s.auth)
  const location = useLocation()

  if (!hydrated) return null

  if (!session) {
    const from = `${location.pathname}${location.search}`
    return (
      <Navigate to={`/portal/sign-in?from=${encodeURIComponent(from)}`} replace />
    )
  }

  return <>{children}</>
}

/**
 * The mirror image: keeps a signed-in user off the auth screens, so /sign-in
 * doesn't render a pointless form to someone who is already in.
 *
 * This also owns the post-sign-in redirect. The auth pages deliberately do NOT
 * navigate themselves: dispatching `signedIn` re-renders this wrapper while the
 * page is still mounted, so a page-level navigate() would race this one and
 * usually lose — which silently dropped the ?from= destination.
 */
export function RedirectIfSignedIn({
  children,
  fallback = '/schedule',
  audience = 'admin',
}: {
  children: ReactNode
  /** Where to land when there's no ?from= — the portal's sign-in lands on /portal. */
  fallback?: string
  /** Whose auth page this is. Each side's pages send the other side home. */
  audience?: Role
}) {
  const { session, hydrated } = useAppSelector((s) => s.auth)
  const [searchParams] = useSearchParams()

  if (!hydrated) return null
  if (session) {
    // Staff only have the portal, whatever ?from= says. An admin on a staff
    // auth page goes back to the admin app, not into the staff view.
    const to =
      session.user.role === 'staff'
        ? '/portal'
        : audience === 'staff'
          ? '/schedule'
          : safeFrom(searchParams.get('from'), fallback)
    return <Navigate to={to} replace />
  }

  return <>{children}</>
}

/**
 * `from` comes off the URL, so it's attacker-controllable: without this,
 * /sign-in?from=https://evil.example sends the user off-site the moment they
 * authenticate. Only same-site absolute paths are honoured — and `//host` is
 * protocol-relative, which the browser treats as another origin.
 */
function safeFrom(from: string | null, fallback: string): string {
  if (!from || !from.startsWith('/') || from.startsWith('//')) return fallback
  return from
}
