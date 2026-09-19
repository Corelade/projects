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
    refresh: '/auth/refresh',
  },
  staff: {
    list: '/list_staff',
    create: '/create_staff',
    update: (id: number) => `/staff/${id}`,
    remove: (id: number) => `/staff/${id}`,
    // Invite links — disabled while staff emails are placeholders.
    // invite: (id: number) => `/staff/${id}/invite`,
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
  /** The staff-facing side: sign-in, invite set-up, and their own rota. */
  portal: {
    signIn: '/portal/login',
    accountStatus: '/portal/account-status',
    createPassword: '/portal/create-password',
    resetPassword: '/portal/reset-password',
    // Invite links — disabled while staff emails are placeholders.
    // invite: (token: string) => `/portal/invite?token=${encodeURIComponent(token)}`,
    // setup: '/portal/setup',
    profile: (staffId?: number) =>
      staffId === undefined ? '/portal/me' : `/portal/me?staff_id=${staffId}`,
    week: (weekStart: string, staffId?: number) =>
      `/portal/schedule?week_start=${weekStart}` +
      (staffId === undefined ? '' : `&staff_id=${staffId}`),
    requests: '/portal/availability-requests',
    cancelRequest: (id: number) => `/portal/availability-requests/${id}/cancel`,
    notifications: '/portal/notifications',
    readNotifications: '/portal/notifications/read',
  },
  /** Admin side of availability change requests. */
  requests: {
    list: (status?: string) =>
      status ? `/availability-requests?status=${status}` : '/availability-requests',
    approve: (id: number) => `/availability-requests/${id}/approve`,
    reject: (id: number) => `/availability-requests/${id}/reject`,
  },
  notifications: {
    list: '/notifications',
    read: '/notifications/read',
  },
  /** WebSocket path for AskAI. ws(s):// is derived from VITE_API_BASE_URL. */
  chat: {
    socket: '/chat_ws',
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
