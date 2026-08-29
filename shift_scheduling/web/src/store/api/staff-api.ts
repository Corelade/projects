import type { Staff, StaffInput } from '@/types'
import { baseApi } from './base-api'
import { ENDPOINTS, METHODS } from './endpoints'
import type { Day, Position, Shift } from '@/types'

interface RawStaff {
  id: number
  first_name: string
  last_name: string
  position: Position
  contract_hours: number
  min_hours: number
  email: string
  exclusions: {
    id: number
    type: 'day' | 'shift'
    value: string
  }[]
}

export const staffApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getStaff: build.query<Staff[], void>({
      query: () => ({ url: ENDPOINTS.staff.list }),

      // extraOptions: { mock: 'staff.list' },
      transformResponse: (rows: RawStaff[]): Staff[] =>
        rows.map((row) => ({
          id: row.id,
          first_name: row.first_name,
          last_name: row.last_name,
          email: row.email,
          position: row.position,
          contract_hours: row.contract_hours,

          // Add this if the backend provides it;
          // otherwise you'll need to decide what the frontend default should be.
          min_hours: row.min_hours,

          day_exclusions: row.exclusions
            .filter((exclusion) => exclusion.type === 'day')
            .map((exclusion) => exclusion.value as Day),

          shift_exclusions: row.exclusions
            .filter((exclusion) => exclusion.type === 'shift')
            .map((exclusion) => exclusion.value as Shift),
        })),

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
      // extraOptions: { mock: 'staff.create' },
      // Rotas reference staff, so a roster change can invalidate a rota.
      invalidatesTags: [{ type: 'Staff', id: 'LIST' }, 'Schedule'],
    }),

    updateStaff: build.mutation<Staff, Staff>({
      query: (body) => ({
        url: ENDPOINTS.staff.update(body.id),
        method: METHODS.update,
        body,
      }),
      // extraOptions: { mock: 'staff.update' },
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
      // extraOptions: { mock: 'staff.remove' },
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
