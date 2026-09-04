import { jwtDecode } from 'jwt-decode'

import { baseApi } from './base-api'
import { ENDPOINTS, METHODS } from './endpoints'

export interface Credentials {
  username: string
  password: string
}

export interface AuthUser {
  id: number
  username: string
}

/** Exactly what the server sends: backend/structs/auth_struct.py AuthResponse. */
interface RawAuth {
  token: string
  user: AuthUser
}

/**
 * What sign-in hands the store. Shaped to match `Session` in auth-slice.ts so the
 * page can dispatch it straight through.
 */
export interface AuthResult {
  token: string
  user: AuthUser
  /** Epoch ms, read out of the token. Null when the token carries no usable `exp`. */
  expiresAt: number | null
}

/**
 * The backend doesn't send an expiry field — AuthResponse is just {token, user}.
 * The deadline lives inside the JWT: `create_access_token` sets `exp`, which PyJWT
 * encodes as epoch *seconds*.
 *
 * This only *reads* the token; it does not verify the signature, and can't — the
 * secret lives on the server. Treat the result as a UX hint that saves a doomed
 * request, never as proof the session is valid. The server stays the authority.
 *
 * Returns null for anything unreadable: jwtDecode throws on a malformed token, and
 * an opaque token must degrade to "no expiry" rather than break sign-in. Null is
 * already what auth-slice.ts treats as "no expiry given".
 */
export function jwtExpiry(token: string): number | null {
  try {
    const { exp } = jwtDecode(token)
    // Seconds -> milliseconds. Skipping this reads as 1970 and expires instantly.
    return typeof exp === 'number' && Number.isFinite(exp) ? exp * 1000 : null
  } catch {
    return null
  }
}

// interface SignupResult {
//   'success': boolean
//   'message': string
// }

export const authApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    signIn: build.mutation<AuthResult, Credentials>({
      query: (body) => ({
        url: ENDPOINTS.auth.signIn,
        method: METHODS.create,
        body,
      }),
      transformResponse: (raw: RawAuth): AuthResult => ({
        token: raw.token,
        user: raw.user,
        expiresAt: jwtExpiry(raw.token),
      }),
    }),

    signUp: build.mutation<void, Credentials>({
      query: (body) => ({
        url: ENDPOINTS.auth.signUp,
        method: METHODS.create,
        body,
      }),
    }), 
  }),
})

export const { useSignInMutation, useSignUpMutation } = authApi
