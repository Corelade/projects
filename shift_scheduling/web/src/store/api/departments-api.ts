import type { Department, DepartmentInput } from '@/types'
import { baseApi } from './base-api'
import { ENDPOINTS, METHODS } from './endpoints'

export const departmentsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getDepartments: build.query<Department[], void>({
      query: () => ({ url: ENDPOINTS.departments.list }),
      // extraOptions: { mock: 'departments.list' },
      /**
       * The ORM calls these name / min_staff / max_staff while the solver calls
       * them name / min_staff / max_staff. If the endpoint
       * returns the ORM spelling, map it here:
       *
       *   transformResponse: (rows) => rows.map(r => ({
       *     id: r.id,
       *     name: r.name,
       *     min_staff: r.min_staff,
       *     max_staff: r.max_staff,
       *   }))
       */
      providesTags: (result) =>
        result
          ? [
              ...result.map((d) => ({ type: 'Department' as const, id: d.id })),
              { type: 'Department' as const, id: 'LIST' },
            ]
          : [{ type: 'Department' as const, id: 'LIST' }],
    }),

    createDepartment: build.mutation<Department, DepartmentInput>({
      query: (body) => ({
        url: ENDPOINTS.departments.create,
        method: METHODS.create,
        body,
      }),
      // extraOptions: { mock: 'departments.create' },
      invalidatesTags: [{ type: 'Department', id: 'LIST' }, 'Schedule'],
    }),

    updateDepartment: build.mutation<Department, Department>({
      query: (body) => ({
        url: ENDPOINTS.departments.update(body.id),
        method: METHODS.update,
        body,
      }),
      // extraOptions: { mock: 'departments.update' },
      invalidatesTags: (_r, _e, arg) => [
        { type: 'Department', id: arg.id },
        { type: 'Department', id: 'LIST' },
        'Schedule',
      ],
    }),

    deleteDepartment: build.mutation<{ id: number }, number>({
      query: (id) => ({
        url: ENDPOINTS.departments.remove(id),
        method: METHODS.remove,
        body: { id },
      }),
      // extraOptions: { mock: 'departments.remove' },
      invalidatesTags: [{ type: 'Department', id: 'LIST' }, 'Schedule'],
    }),
  }),
})

export const {
  useGetDepartmentsQuery,
  useCreateDepartmentMutation,
  useUpdateDepartmentMutation,
  useDeleteDepartmentMutation,
} = departmentsApi
