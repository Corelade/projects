import type { Staff, StaffInput } from '@/types'
import { baseApi } from './base-api'
import { ENDPOINTS, METHODS } from './endpoints'

export const staffApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getStaff: build.query<Staff[], void>({
      query: () => ({ url: ENDPOINTS.staff.list }),
      extraOptions: { mock: 'staff.list' },
      /**
       * If the backend returns a different shape, normalise it HERE — not in
       * components. e.g. exclusions arriving as [{type, value}] rows:
       *
       *   transformResponse: (rows: RawStaff[]) => rows.map(fromRawStaff)
       */
      providesTags: (result) =>
        result
          ? [
              ...result.map((s) => ({ type: 'Staff' as const, id: s.id })),
              { type: 'Staff' as const, id: 'LIST' },
            ]
          : [{ type: 'Staff' as const, id: 'LIST' }],
    }),

    createStaff: build.mutation<Staff, StaffInput>({
      query: (body) => ({
        url: ENDPOINTS.staff.create,
        method: METHODS.create,
        body,
      }),
      extraOptions: { mock: 'staff.create' },
      // Rotas reference staff, so a roster change can invalidate a rota.
      invalidatesTags: [{ type: 'Staff', id: 'LIST' }, 'Schedule'],
    }),

    updateStaff: build.mutation<Staff, Staff>({
      query: (body) => ({
        url: ENDPOINTS.staff.update(body.id),
        method: METHODS.update,
        body,
      }),
      extraOptions: { mock: 'staff.update' },
      invalidatesTags: (_r, _e, arg) => [
        { type: 'Staff', id: arg.id },
        { type: 'Staff', id: 'LIST' },
        'Schedule',
      ],
    }),

    deleteStaff: build.mutation<{ id: number }, number>({
      query: (id) => ({
        url: ENDPOINTS.staff.remove(id),
        method: METHODS.remove,
        body: { id },
      }),
      extraOptions: { mock: 'staff.remove' },
      invalidatesTags: [{ type: 'Staff', id: 'LIST' }, 'Schedule'],
    }),
  }),
})

export const {
  useGetStaffQuery,
  useCreateStaffMutation,
  useUpdateStaffMutation,
  useDeleteStaffMutation,
} = staffApi
