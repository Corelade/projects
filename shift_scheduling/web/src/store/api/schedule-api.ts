import type { ScheduleCell, ScheduleWeek, UpdateCellRequest } from '@/types'
import { baseApi } from './base-api'
import { ENDPOINTS, METHODS } from './endpoints'
import type { Day, Shift } from '../../types/common'
import type { Assignment } from '@/types'


interface RawScheduleResponse {
  week_start: string
  week_end: string
  generated_at: string | null
  schedule: Record<
    string,
    Record<
      string,
      Record<Shift, Assignment[]>
    >
  >
}

export const scheduleApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getWeek: build.query<ScheduleWeek, string>({
      query: (weekStart) => ({
        url: ENDPOINTS.schedule.week(weekStart),
        // body: { week_start: weekStart }, 
      }),
      // extraOptions: { mock: 'schedule.week' },
      /**
       * The solver's own result is nested day -> department -> shift -> [name]
       * and, via to_normal_dict (app.py:111), carries no IDs. The UI needs IDs
       * to edit a cell, so normalise into the flat `cells` array HERE — a flat
       * list is far easier to index, diff and optimistically patch.
       *
       *   transformResponse: (raw: NestedSchedule) => flattenWeek(raw)
       */

      transformResponse: (raw: RawScheduleResponse): ScheduleWeek => {
        const cells: ScheduleCell[] = []

        for (const [day, departments] of Object.entries(raw.schedule)) {
          for (const [departmentId, shifts] of Object.entries(departments)) {
            for (const [shift, staff] of Object.entries(shifts)) {
              cells.push({
                department_id: Number(departmentId),
                day: day as Day,
                shift: shift as Shift,
                staff,
              })
            }
          }
        }

        return {
          week_start: raw.week_start,
          week_end: raw.week_end,
          generated_at: raw.generated_at,
          cells,
        }
      },
      providesTags: (_r, _e, weekStart) => [{ type: 'Schedule', id: weekStart }],
    }),

    generateWeek: build.mutation<ScheduleWeek, string>({
      query: (weekStart) => ({
        url: ENDPOINTS.schedule.generate,
        method: METHODS.generate,
        body: { week_start: weekStart },
      }),
      // extraOptions: { mock: 'schedule.generate' },
      invalidatesTags: (_r, _e, weekStart) => [
        { type: 'Schedule', id: weekStart },
      ],
    }),

    updateCell: build.mutation<ScheduleCell, UpdateCellRequest>({
      query: (body) => ({
        url: ENDPOINTS.schedule.updateCell,
        method: METHODS.updateCell,
        body,
      }),
      // extraOptions: { mock: 'schedule.updateCell' },

      /**
       * Optimistic: assigning someone should feel like moving a magnet on a
       * whiteboard. Rolls back on failure (docs/ui/04-patterns.md).
       */
      async onQueryStarted(patch, { dispatch, queryFulfilled }) {
        const undo = dispatch(
          scheduleApi.util.updateQueryData(
            'getWeek',
            patch.week_start,
            (draft) => {
              const cell = draft.cells.find(
                (c) =>
                  c.department_id === patch.department_id &&
                  c.day === patch.day &&
                  c.shift === patch.shift,
              )
              if (cell) {
                cell.staff = patch.staff_ids.map((id) => {
                  const existing = draft.cells
                    .flatMap((c) => c.staff)
                    .find((a) => a.staff_id === id)
                  return {
                    staff_id: id,
                    staff_name: existing?.staff_name ?? '…',
                  }
                })
              }
            },
          ),
        )
        try {
          await queryFulfilled
        } catch {
          undo.undo()
        }
      },
      // No invalidation — the patch above is the update.
    }),
  }),
})

export const {
  useGetWeekQuery,
  useGenerateWeekMutation,
  useUpdateCellMutation,
} = scheduleApi
