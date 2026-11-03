import { createContext, useContext } from 'react'
import type { User } from '../types/api'

export interface CurrentUserState {
  user: User | null
  logIn(user: User): void
  logOut(): void
}

export const CurrentUserContext = createContext<CurrentUserState | null>(null)

export function useCurrentUser(): CurrentUserState {
  const state = useContext(CurrentUserContext)
  if (state === null) {
    throw new Error('useCurrentUser must be used inside <CurrentUserProvider>.')
  }
  return state
}

/** The logged-in user; only for pages behind <RequireUser>, where a user always exists. */
export function useLoggedInUser(): User {
  const { user } = useCurrentUser()
  if (user === null) {
    throw new Error('useLoggedInUser must be used on a page behind <RequireUser>.')
  }
  return user
}
