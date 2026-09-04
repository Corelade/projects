import {
  createApi,
  fetchBaseQuery,
  type BaseQueryFn,
  type FetchArgs,
  type FetchBaseQueryError,
} from '@reduxjs/toolkit/query/react'

import { handleMock, type MockKey } from '@/mocks'
import { signedOut } from '../slices/auth-slice'

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true'

export interface ApiExtraOptions {
  /** Which mock handler serves this endpoint when VITE_USE_MOCKS=true. */
  mock?: MockKey
}

const realBaseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },

  /**
   * The backend guards routes with `Depends(get_current_user)`, so every request
   * past sign-in needs the token. Only set it when a session exists — /auth/login
   * and /auth/signup must go out bare, and `Bearer undefined` is worse than no
   * header at all.
   *
   * getState() is typed inline rather than as RootState on purpose: store/index.ts
   * imports baseApi, so importing RootState back into this file is a cycle.
   */
  prepareHeaders: (headers, { getState }) => {
    const { session } = (
      getState() as { auth: { session: { token: string } | null } }
    ).auth
    if (session) headers.set('Authorization', `Bearer ${session.token}`)
    return headers
  },
})

/**
 * Swaps in the fixture layer when VITE_USE_MOCKS=true, so the whole UI is
 * reviewable before any endpoint exists. Set the flag to false to go live —
 * that plus the paths in endpoints.ts is the entire switch.
 */
const baseQuery: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError,
  ApiExtraOptions
> = async (args, api, extraOptions) => {
  if (USE_MOCKS && extraOptions?.mock) {
    const body = typeof args === 'string' ? undefined : args.body
    const result = await handleMock(extraOptions.mock, body)
    if (result.error) {
      return { error: result.error as FetchBaseQueryError }
    }
    return { data: result.data }
  }
  const result = await realBaseQuery(args, api, extraOptions)
  if (result.error?.status === 401){
    api.dispatch(signedOut())
  }
  return result
}

export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery,
  tagTypes: ['Staff', 'Department', 'Schedule'],
  endpoints: () => ({}),
})

/** Pull a readable message out of whatever the server returned. */
export function errorMessage(error: unknown, fallback = 'Something went wrong.'): string {
  if (!error) return fallback
  const e = error as FetchBaseQueryError & { data?: unknown }

  if (typeof e.status === 'number' && e.data) {
    const data = e.data as { detail?: unknown; message?: unknown }
    if (typeof data.detail === 'string') return data.detail
    if (typeof data.message === 'string') return data.message
    // FastAPI validation errors arrive as a list of {loc, msg}.
    if (Array.isArray(data.detail)) {
      const first = data.detail[0] as { msg?: string } | undefined
      if (first?.msg) return first.msg
    }
  }
  if (e.status === 'FETCH_ERROR') {
    console.log(e)
    return "Try again later"
  }
  return fallback
}
