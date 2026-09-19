import type {
  ApproveRequestArgs,
  AvailabilityRequest,
  AvailabilityRequestInput,
  RejectRequestArgs,
  RequestStatus,
} from '@/types'
import { baseApi } from './base-api'
import { ENDPOINTS, METHODS } from './endpoints'

/**
 * Availability change requests. Staff make them from the portal; the admin
 * approves (optionally adjusted) or rejects from /requests. Either side's
 * action notifies the other, so both invalidate Notification too.
 */
export const requestsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    // --- admin

    getAvailabilityRequests: build.query<AvailabilityRequest[], RequestStatus | void>({
      query: (status) => ({ url: ENDPOINTS.requests.list(status ?? undefined) }),
      providesTags: ['AvailabilityRequest'],
    }),

    approveRequest: build.mutation<AvailabilityRequest, ApproveRequestArgs>({
      query: ({ id, ...body }) => ({
        url: ENDPOINTS.requests.approve(id),
        method: METHODS.create,
        body,
      }),
      // Approving changes the staff member's availability.
      invalidatesTags: ['AvailabilityRequest', 'Staff', 'Portal'],
    }),

    rejectRequest: build.mutation<AvailabilityRequest, RejectRequestArgs>({
      query: ({ id, ...body }) => ({
        url: ENDPOINTS.requests.reject(id),
        method: METHODS.create,
        body,
      }),
      invalidatesTags: ['AvailabilityRequest'],
    }),

    // --- staff

    getMyRequests: build.query<AvailabilityRequest[], void>({
      query: () => ({ url: ENDPOINTS.portal.requests }),
      providesTags: ['AvailabilityRequest'],
    }),

    requestAvailabilityChange: build.mutation<AvailabilityRequest, AvailabilityRequestInput>({
      query: (body) => ({
        url: ENDPOINTS.portal.requests,
        method: METHODS.create,
        body,
      }),
      invalidatesTags: ['AvailabilityRequest'],
    }),

    cancelRequest: build.mutation<AvailabilityRequest, number>({
      query: (id) => ({
        url: ENDPOINTS.portal.cancelRequest(id),
        method: METHODS.create,
      }),
      invalidatesTags: ['AvailabilityRequest'],
    }),
  }),
})

export const {
  useGetAvailabilityRequestsQuery,
  useApproveRequestMutation,
  useRejectRequestMutation,
  useGetMyRequestsQuery,
  useRequestAvailabilityChangeMutation,
  useCancelRequestMutation,
} = requestsApi
