import type { NotificationList } from '@/types'
import { baseApi } from './base-api'
import { ENDPOINTS, METHODS } from './endpoints'

/**
 * In-app notifications. No polling: they're fetched when a page loads (or is
 * refreshed), and refetched after the viewer's own actions via the
 * Notification tag. Something meant for the other side shows up on their next
 * page load.
 *
 * Admin and staff read from separate endpoints — each only accepts its own
 * kind of token.
 */
export const notificationsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getNotifications: build.query<NotificationList, void>({
      query: () => ({ url: ENDPOINTS.notifications.list }),
      providesTags: ['Notification'],
    }),

    /** No ids marks everything read. */
    markNotificationsRead: build.mutation<void, number[] | void>({
      query: (ids) => ({
        url: ENDPOINTS.notifications.read,
        method: METHODS.create,
        body: { ids: ids ?? null },
      }),
      invalidatesTags: ['Notification'],
    }),

    getPortalNotifications: build.query<NotificationList, void>({
      query: () => ({ url: ENDPOINTS.portal.notifications }),
      providesTags: ['Notification'],
    }),

    markPortalNotificationsRead: build.mutation<void, number[] | void>({
      query: (ids) => ({
        url: ENDPOINTS.portal.readNotifications,
        method: METHODS.create,
        body: { ids: ids ?? null },
      }),
      invalidatesTags: ['Notification'],
    }),
  }),
})

export const {
  useGetNotificationsQuery,
  useMarkNotificationsReadMutation,
  useGetPortalNotificationsQuery,
  useMarkPortalNotificationsReadMutation,
} = notificationsApi
