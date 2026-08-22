import { Navigate, Route, Routes } from 'react-router'

import ToastStack from '@/components/toast/toast'
import DepartmentsPage from '@/pages/departments/departments'
import SchedulePage from '@/pages/schedule/schedule'
import StaffPage from '@/pages/staff/staff'

/**
 * Drawer routes are nested children of their list route, so the list stays
 * mounted behind the drawer and Back closes it.
 */
export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/schedule" replace />} />
        <Route path="/schedule" element={<SchedulePage />} />

        <Route path="/staff" element={<StaffPage />}>
          <Route path="new" element={null} />
          <Route path=":id/edit" element={null} />
        </Route>

        <Route path="/departments" element={<DepartmentsPage />}>
          <Route path="new" element={null} />
          <Route path=":id/edit" element={null} />
        </Route>

        <Route path="*" element={<Navigate to="/schedule" replace />} />
      </Routes>
      <ToastStack />
    </>
  )
}
