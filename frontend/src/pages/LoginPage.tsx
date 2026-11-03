import { useState, type ChangeEvent, type FormEvent, type ReactElement } from 'react'
import { Navigate } from 'react-router'
import { describeError } from '../api/client'
import { createUser, listUsers } from '../api/endpoints'
import { ErrorMessage } from '../components/ErrorMessage'
import { useCurrentUser } from '../context/currentUser'
import { useApiData } from '../hooks/useApiData'
import type { User } from '../types/api'

/** "Log in as…": pick an existing user or create a new one (no passwords, see AGENTS.md §4). */
export function LoginPage(): ReactElement {
  const { user, logIn } = useCurrentUser()
  const users = useApiData(listUsers)
  const [selectedUserId, setSelectedUserId] = useState('')
  const [newUserName, setNewUserName] = useState('')
  const [createError, setCreateError] = useState<string | null>(null)

  if (user !== null) {
    return <Navigate to="/" replace />
  }

  function handleUserChange(event: ChangeEvent<HTMLSelectElement>): void {
    setSelectedUserId(event.target.value)
  }

  function handleNameChange(event: ChangeEvent<HTMLInputElement>): void {
    setNewUserName(event.target.value)
  }

  function isSelectedUser(candidate: User): boolean {
    return String(candidate.id) === selectedUserId
  }

  function handleLogIn(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    const chosenUser = users.data?.find(isSelectedUser)
    if (chosenUser !== undefined) {
      logIn(chosenUser)
    }
  }

  async function handleCreateUser(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    try {
      logIn(await createUser(newUserName.trim()))
    } catch (error) {
      setCreateError(describeError(error))
    }
  }

  return (
    <main className="narrow">
      <h1>Log in</h1>
      <ErrorMessage message={users.error} />
      <form onSubmit={handleLogIn}>
        <label htmlFor="login-user">User</label>
        <select id="login-user" value={selectedUserId} onChange={handleUserChange} required>
          <option value="" disabled>
            Choose a user…
          </option>
          {users.data?.map(renderUserOption)}
        </select>
        <button type="submit">Log in</button>
      </form>

      <h2>New user</h2>
      <form onSubmit={handleCreateUser}>
        <label htmlFor="new-user-name">Name</label>
        <input id="new-user-name" value={newUserName} onChange={handleNameChange} required />
        <button type="submit">Create and log in</button>
      </form>
      <ErrorMessage message={createError} />
    </main>
  )
}

function renderUserOption(user: User): ReactElement {
  return (
    <option key={user.id} value={user.id}>
      {user.name}
    </option>
  )
}
