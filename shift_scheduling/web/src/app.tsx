import { Navigate, Route, Routes } from 'react-router'

import ToastStack from '@/components/toast/toast'
import SignInPage from '@/pages/auth/sign-in'
import SignUpPage from '@/pages/auth/sign-up'
import DepartmentsPage from '@/pages/departments/departments'
import HomePage from '@/pages/home/home'
import SchedulePage from '@/pages/schedule/schedule'
import StaffPage from '@/pages/staff/staff'
import RequireAuth, { RedirectIfSignedIn } from '@/routes/require-auth'

/**
 * `/` is public and unguarded — it's the marketing page, and it renders for
 * signed-in visitors too, with its calls to action pointing at the rota.
 *
 * Drawer routes are nested children of their list route, so the list stays
 * mounted behind the drawer and Back closes it.
 *
 * The auth routes sit outside the app shell — no sidebar, no topbar — and are
 * wrapped in RedirectIfSignedIn. Every app route sits behind RequireAuth, which
 * redirects to /sign-in?from=<path> when there's no session.
 */
export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />

        <Route
          path="/sign-in"
          element={
            <RedirectIfSignedIn>
              <SignInPage />
            </RedirectIfSignedIn>
          }
        />
        <Route
          path="/sign-up"
          element={
            <RedirectIfSignedIn>
              <SignUpPage />
            </RedirectIfSignedIn>
          }
        />

        <Route
          path="/schedule"
          element={
            <RequireAuth>
              <SchedulePage />
            </RequireAuth>
          }
        />

        <Route
          path="/staff"
          element={
            <RequireAuth>
              <StaffPage />
            </RequireAuth>
          }
        >
          <Route path="new" element={null} />
          <Route path=":id/edit" element={null} />
        </Route>

        <Route
          path="/departments"
          element={
            <RequireAuth>
              <DepartmentsPage />
            </RequireAuth>
          }
        >
          <Route path="new" element={null} />
          <Route path=":id/edit" element={null} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <ToastStack />
    </>
  )
}
