import { useEffect } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router'

import AskAiPanel from '@/components/ask-ai/ask-ai-panel'
import ToastStack from '@/components/toast/toast'
import SignInPage from '@/pages/auth/sign-in'
import SignUpPage from '@/pages/auth/sign-up'
import DepartmentsPage from '@/pages/departments/departments'
import HomePage from '@/pages/home/home'
import PortalPage from '@/pages/portal/portal'
import PortalPasswordPage from '@/pages/portal/portal-password'
// Invite links — disabled while staff emails are placeholders.
// import PortalSetupPage from '@/pages/portal/portal-setup'
import PortalSignInPage from '@/pages/portal/portal-sign-in'
import RequestsPage from '@/pages/requests/requests'
import SchedulePage from '@/pages/schedule/schedule'
import StaffPage from '@/pages/staff/staff'
import RequireAuth, { RedirectIfSignedIn, RequirePortal } from '@/routes/require-auth'
import { useSessionKeepAlive } from '@/routes/use-session-keep-alive'
import { useAppDispatch, useAppSelector } from '@/store'
import { setAskAiOpen } from '@/store/slices/ui-slice'

/** Routes outside the app shell, where AskAI has no sidebar entry to open it. */
const NO_ASK_AI = ['/', '/sign-in', '/sign-up']

/** The staff portal has its own shell, and AskAI is an admin tool. */
const isPortal = (pathname: string) =>
  pathname === '/portal' || pathname.startsWith('/portal/')

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
  const isAdmin = useAppSelector((s) => s.auth.session?.user.role === 'admin')
  const dispatch = useAppDispatch()
  const outsideShell = NO_ASK_AI.includes(pathname) || isPortal(pathname)

  useSessionKeepAlive()

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

        <Route
          path="/requests"
          element={
            <RequireAuth>
              <RequestsPage />
            </RequireAuth>
          }
        />

        {/* Staff portal: staff see their own rota; admins can view any of theirs. */}
        <Route
          path="/portal/sign-in"
          element={
            <RedirectIfSignedIn fallback="/portal" audience="staff">
              <PortalSignInPage />
            </RedirectIfSignedIn>
          }
        />
        <Route
          path="/portal/create-password"
          element={
            <RedirectIfSignedIn fallback="/portal" audience="staff">
              <PortalPasswordPage key="create" mode="create" />
            </RedirectIfSignedIn>
          }
        />
        <Route
          path="/portal/forgot-password"
          element={
            <RedirectIfSignedIn fallback="/portal" audience="staff">
              <PortalPasswordPage key="reset" mode="reset" />
            </RedirectIfSignedIn>
          }
        />
        {/* Invite links — disabled while staff emails are placeholders.
        <Route path="/portal/setup" element={<PortalSetupPage />} /> */}
        <Route
          path="/portal"
          element={
            <RequirePortal>
              <PortalPage />
            </RequirePortal>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      {/* Mounted here, not in Layout, so the chat survives page changes. */}
      {isAdmin && <AskAiPanel />}
      <ToastStack />
    </>
  )
}
