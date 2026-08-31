import type { ReactNode } from 'react'
import { Navigate, useLocation, useSearchParams } from 'react-router'

import { useAppSelector } from '@/store'

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
export function RedirectIfSignedIn({ children }: { children: ReactNode }) {
  const { session, hydrated } = useAppSelector((s) => s.auth)
  const [searchParams] = useSearchParams()

  if (!hydrated) return null
  if (session) return <Navigate to={safeFrom(searchParams.get('from'))} replace />

  return <>{children}</>
}

/**
 * `from` comes off the URL, so it's attacker-controllable: without this,
 * /sign-in?from=https://evil.example sends the user off-site the moment they
 * authenticate. Only same-site absolute paths are honoured — and `//host` is
 * protocol-relative, which the browser treats as another origin.
 */
function safeFrom(from: string | null): string {
  if (!from || !from.startsWith('/') || from.startsWith('//')) return '/schedule'
  return from
}
