/**
 * ============================================================================
 *  THE ENDPOINT MAP
 * ============================================================================
 *
 *  This is the ONLY file in the app that contains a URL. When the backend
 *  routes are built, edit the paths here and nothing else.
 *
 *  `staff.list`, `staff.create`, `departments.list` and `departments.create`
 *  match the routes that exist in api.py today. Everything else is a
 *  placeholder — rename to whatever you build.
 *
 *  If a response shape differs from what the UI expects, fix it in that
 *  endpoint's `transformResponse` (see staff-api.ts) rather than reshaping
 *  components.
 */

export const ENDPOINTS = {
  // Placeholders — no auth routes exist on the backend yet. Rename these to
  // whatever you build; nothing outside this file needs to change.
  auth: {
    signIn: '/auth/login',
    signUp: '/auth/signup',
  },
  staff: {
    list: '/list_staff',
    create: '/create_staff',
    update: (id: number) => `/staff/${id}`,
    remove: (id: number) => `/staff/${id}`,
  },
  departments: {
    list: '/departments',
    create: '/create_department',
    update: (id: number) => `/departments/${id}`,
    remove: (id: number) => `/departments/${id}`,
  },
  schedule: {
    week: (weekStart: string) => `/schedule?week_start=${weekStart}`,
    generate: '/schedule/generate',
    updateCell: '/schedule/update',
  },
} as const

/** HTTP verbs, kept here so a backend that prefers PUT over PATCH is a one-line change. */
export const METHODS = {
  create: 'POST',
  update: 'PATCH',
  remove: 'DELETE',
  generate: 'POST',
  updateCell: 'POST',
} as const
