import type {
  AccountStatus,
  PortalProfile,
  PortalWeek,
  PortalWeekArgs,
} from '@/types'
import { toAuthResult, type AuthResult } from './auth-api'
import { baseApi } from './base-api'
import { ENDPOINTS, METHODS } from './endpoints'

/** Staff only — admins sign in through /auth/login. */
export interface PortalCredentials {
  email: string
  password: string
}

/** Create password (first time) or forgot password (set a new one). */
export interface PasswordRequest {
  email: string
  password: string
}

export const portalApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    portalSignIn: build.mutation<AuthResult, PortalCredentials>({
      query: (body) => ({
        url: ENDPOINTS.portal.signIn,
        method: METHODS.create,
        body,
      }),
      transformResponse: toAuthResult,
    }),

    /** 404s for an email no staff member has. */
    checkAccount: build.mutation<AccountStatus, string>({
      query: (email) => ({
        url: ENDPOINTS.portal.accountStatus,
        method: METHODS.create,
        body: { email },
      }),
    }),

    /** First-time password; signs them straight in. 409s if they already have one. */
    createPassword: build.mutation<AuthResult, PasswordRequest>({
      query: (body) => ({
        url: ENDPOINTS.portal.createPassword,
        method: METHODS.create,
        body,
      }),
      transformResponse: toAuthResult,
    }),

    /** Forgot password; signs them straight in. 409s if they never made one. */
    resetPassword: build.mutation<AuthResult, PasswordRequest>({
      query: (body) => ({
        url: ENDPOINTS.portal.resetPassword,
        method: METHODS.create,
        body,
      }),
      transformResponse: toAuthResult,
    }),

    // Invite links — disabled while staff emails are placeholders.
    // getInvite: build.query<InviteDetails, string>({
    //   query: (token) => ({ url: ENDPOINTS.portal.invite(token) }),
    // }),
    // setupAccount: build.mutation<AuthResult, AccountSetup>({
    //   query: (body) => ({ url: ENDPOINTS.portal.setup, method: METHODS.create, body }),
    //   transformResponse: toAuthResult,
    // }),

    getPortalProfile: build.query<PortalProfile, number | undefined>({
      query: (staffId) => ({ url: ENDPOINTS.portal.profile(staffId) }),
      providesTags: ['Portal'],
    }),

    getPortalWeek: build.query<PortalWeek, PortalWeekArgs>({
      query: ({ weekStart, staffId }) => ({
        url: ENDPOINTS.portal.week(weekStart, staffId),
      }),
      providesTags: ['Portal'],
    }),
  }),
})

export const {
  usePortalSignInMutation,
  useCheckAccountMutation,
  useCreatePasswordMutation,
  useResetPasswordMutation,
  useGetPortalProfileQuery,
  useGetPortalWeekQuery,
} = portalApi
