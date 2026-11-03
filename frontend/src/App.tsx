import type { ReactElement } from 'react'
import { Navigate, Route, Routes } from 'react-router'
import { RequireUser } from './components/RequireUser'
import { GroupDetailPage } from './pages/GroupDetailPage'
import { GroupListPage } from './pages/GroupListPage'
import { LoginPage } from './pages/LoginPage'

export function App(): ReactElement {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireUser />}>
        <Route path="/" element={<GroupListPage />} />
        <Route path="/groups/:groupId" element={<GroupDetailPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
