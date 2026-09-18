import { useEffect } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router'

import AskAiPanel from '@/components/ask-ai/ask-ai-panel'
import ToastStack from '@/components/toast/toast'
import SignInPage from '@/pages/auth/sign-in'
import SignUpPage from '@/pages/auth/sign-up'
import DepartmentsPage from '@/pages/departments/departments'
import HomePage from '@/pages/home/home'
import SchedulePage from '@/pages/schedule/schedule'
import StaffPage from '@/pages/staff/staff'
import RequireAuth, { RedirectIfSignedIn } from '@/routes/require-auth'
import { useAppDispatch, useAppSelector } from '@/store'
import { setAskAiOpen } from '@/store/slices/ui-slice'

/** Routes outside the app shell, where AskAI has no sidebar entry to open it. */
const NO_ASK_AI = ['/', '/sign-in', '/sign-up']

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
  const { pathname } = useLocation()
  const signedIn = useAppSelector((s) => s.auth.session !== null)
  const dispatch = useAppDispatch()
  const outsideShell = NO_ASK_AI.includes(pathname)

  // Stay mounted (history intact) but shut when leaving the app shell.
  useEffect(() => {
    if (outsideShell) dispatch(setAskAiOpen(false))
  }, [outsideShell, dispatch])

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
      {/* Mounted here, not in Layout, so the chat survives page changes. */}
      {signedIn && <AskAiPanel />}
      <ToastStack />
    </>
  )
}
