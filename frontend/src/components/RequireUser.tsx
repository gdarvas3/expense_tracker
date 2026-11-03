import type { ReactElement } from 'react'
import { Navigate, Outlet } from 'react-router'
import { useCurrentUser } from '../context/currentUser'

/** Route guard: pages below it are only shown to a logged-in user. */
export function RequireUser(): ReactElement {
  const { user, logOut } = useCurrentUser()
  if (user === null) {
    return <Navigate to="/login" replace />
  }
  return (
    <>
      <header className="app-header">
        <span className="brand">
          SPLITTER<span className="brand-slash">/</span>
        </span>
        <nav aria-label="Account" className="account">
          <span>Logged in as {user.name}</span>
          <button type="button" onClick={logOut}>
            Log out
          </button>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </>
  )
}
