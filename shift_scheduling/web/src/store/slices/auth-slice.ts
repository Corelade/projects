import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { AuthUser } from '@/store/api/auth-api'

export interface Session {
  token: string
  user: AuthUser
  /** Epoch ms. Null when the server sends no expiry with the token. */
  expiresAt: number | null
}

interface AuthState {
  session: Session | null
  /**
   * False until the stored session has been read back on boot. A route guard
   * needs to tell "no session" apart from "haven't looked yet", or a reload on
   * a protected route flashes the sign-in page on its way back.
   */
  hydrated: boolean
}

const STORAGE_KEY = 'shiftpro.session'

/**
 * The session is mirrored to localStorage so it survives a reload, which means
 * anything that can run JS on this origin can read the token. That is inherent
 * to a bearer-token SPA — the alternative is an httpOnly cookie, which the
 * server would own instead. If sessions should die with the tab (a shared
 * back-office machine, say), swap both calls below for sessionStorage.
 *
 * Storage access is wrapped everywhere: private mode and browsers set to block
 * site data *throw* on access, and taking the app down at boot is a far worse
 * failure than not persisting.
 */
export function readStoredSession(): Session | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null

    const parsed = JSON.parse(raw) as Partial<Session>
    const valid =
      typeof parsed?.token === 'string' &&
      parsed.token.length > 0 &&
      typeof parsed.user?.id === 'number' &&
      typeof parsed.user?.username === 'string'

    // A null expiresAt means "no expiry given" — the server stays the authority
    // and rejects the token when it's spent. Only a real, passed deadline counts.
    const expired =
      typeof parsed?.expiresAt === 'number' && parsed.expiresAt <= Date.now()

    if (!valid || expired) {
      clearStoredSession()
      return null
    }

    return parsed as Session
  } catch {
    // Unreadable storage, or a shape written by an older build.
    return null
  }
}

function writeStoredSession(session: Session) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
  } catch {
    // Storage unavailable or full — the session still works for this tab.
  }
}

function clearStoredSession() {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // Nothing to do; the in-memory session is cleared either way.
  }
}

const initialState: AuthState = {
  session: null,
  hydrated: false,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /** Reads storage once on boot, before the first render decides on a redirect. */
    hydrate(state) {
      state.session = readStoredSession()
      state.hydrated = true
    },
    signedIn(state, action: PayloadAction<Session>) {
      state.session = action.payload
      state.hydrated = true
      writeStoredSession(action.payload)
    },
    signedOut(state) {
      state.session = null
      state.hydrated = true
      clearStoredSession()
    },
  },
})

export const { hydrate, signedIn, signedOut } = authSlice.actions

export default authSlice.reducer
