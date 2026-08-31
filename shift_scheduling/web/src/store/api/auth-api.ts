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

/**
 * What a successful sign-in/sign-up hands back. The token is whatever your
 * backend issues — nothing here stores it yet; see the TODO in sign-in.tsx.
 */
export interface AuthResult {
  token: string
  user: AuthUser
}

export const authApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    signIn: build.mutation<AuthResult, Credentials>({
      query: (body) => ({
        url: ENDPOINTS.auth.signIn,
        method: METHODS.create,
        body,
      }),
      extraOptions: { mock: 'auth.signIn' },
    }),

    signUp: build.mutation<AuthResult, Credentials>({
      query: (body) => ({
        url: ENDPOINTS.auth.signUp,
        method: METHODS.create,
        body,
      }),
      extraOptions: { mock: 'auth.signUp' },
    }),
  }),
})

export const { useSignInMutation, useSignUpMutation } = authApi
