import { useState, type ReactElement, type ReactNode } from 'react'
import type { User } from '../types/api'
import { CurrentUserContext } from './currentUser'
import { clearStoredUser, loadStoredUser, storeUser } from './userStorage'

interface CurrentUserProviderProps {
  children: ReactNode
}

export function CurrentUserProvider({ children }: CurrentUserProviderProps): ReactElement {
  const [user, setUser] = useState<User | null>(loadStoredUser)

  function logIn(nextUser: User): void {
    storeUser(nextUser)
    setUser(nextUser)
  }

  function logOut(): void {
    clearStoredUser()
    setUser(null)
  }

  return <CurrentUserContext value={{ user, logIn, logOut }}>{children}</CurrentUserContext>
}
