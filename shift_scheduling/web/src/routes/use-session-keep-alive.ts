import { useEffect, useRef } from 'react'

import { useAppDispatch, useAppSelector } from '@/store'
import { useRefreshTokenMutation } from '@/store/api/auth-api'
import { signedIn } from '@/store/slices/auth-slice'

/** Refresh once the token has less than this left. */
const REFRESH_WITHIN_MS = 10 * 60_000
/** Activity events fire constantly; look at the clock at most this often. */
const CHECK_EVERY_MS = 60_000

const ACTIVITY_EVENTS = ['pointerdown', 'pointermove', 'keydown', 'scroll', 'visibilitychange']

/**
 * Sliding session. The JWT lives 30 minutes; while the user is actually using
 * the app, swap it for a fresh one before it runs out, so working past the
 * half hour doesn't sign them out. Someone idle for the full 30 minutes still
 * gets signed out on their next request.
 *
 * Activity, not a timer: a timer would keep an abandoned tab signed in forever.
 * A refresh that 401s signs out through base-api.ts like any other request;
 * any other failure is simply retried on later activity.
 */
export function useSessionKeepAlive() {
  const expiresAt = useAppSelector((s) => s.auth.session?.expiresAt ?? null)
  const dispatch = useAppDispatch()
  const [refresh] = useRefreshTokenMutation()

  const inFlight = useRef(false)
  const lastCheck = useRef(0)

  useEffect(() => {
    // No session, or a token without a readable expiry: nothing to keep alive.
    if (expiresAt === null) return
    const deadline = expiresAt

    async function onActivity() {
      const now = Date.now()
      if (inFlight.current || now - lastCheck.current < CHECK_EVERY_MS) return
      lastCheck.current = now
      if (deadline - now > REFRESH_WITHIN_MS) return

      inFlight.current = true
      try {
        dispatch(signedIn(await refresh().unwrap()))
      } catch {
        // See the doc comment: a 401 already signed out, anything else retries.
      } finally {
        inFlight.current = false
      }
    }

    for (const e of ACTIVITY_EVENTS) {
      document.addEventListener(e, onActivity, { capture: true, passive: true })
    }
    return () => {
      for (const e of ACTIVITY_EVENTS) {
        document.removeEventListener(e, onActivity, { capture: true })
      }
    }
  }, [expiresAt, refresh, dispatch])
}
