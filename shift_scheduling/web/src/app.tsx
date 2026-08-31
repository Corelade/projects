import { Navigate, Route, Routes } from 'react-router'

import ToastStack from '@/components/toast/toast'
import SignInPage from '@/pages/auth/sign-in'
import SignUpPage from '@/pages/auth/sign-up'
import DepartmentsPage from '@/pages/departments/departments'
import SchedulePage from '@/pages/schedule/schedule'
import StaffPage from '@/pages/staff/staff'
import RequireAuth, { RedirectIfSignedIn } from '@/routes/require-auth'

/**
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
        <Route path="/" element={<Navigate to="/schedule" replace />} />

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

        <Route path="*" element={<Navigate to="/schedule" replace />} />
      </Routes>
      <ToastStack />
    </>
  )
}
