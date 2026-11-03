import { useState, type ChangeEvent, type FormEvent, type ReactElement } from 'react'
import { Navigate } from 'react-router'
import { createUser, listUsers } from '../api/endpoints'
import { ErrorMessage } from '../components/ErrorMessage'
import { useCurrentUser } from '../context/currentUser'
import { useApiData } from '../hooks/useApiData'
import { useAsyncAction } from '../hooks/useAsyncAction'
import type { User } from '../types/api'

/** "Log in as…": pick an existing user or create a new one (no passwords, see AGENTS.md §4). */
export function LoginPage(): ReactElement {
  const { user, logIn } = useCurrentUser()
  const users = useApiData(listUsers)
  const [selectedUserId, setSelectedUserId] = useState('')
  const [newUserName, setNewUserName] = useState('')
  const creation = useAsyncAction(createAndLogIn)

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

  async function createAndLogIn(name: string): Promise<void> {
    logIn(await createUser(name))
  }

  function handleCreateUser(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    void creation.run(newUserName.trim())
  }

  return (
    <main className="narrow">
      <p className="brand">
        SPLITTER<span className="brand-slash">/</span>
      </p>
      <h1>Log in</h1>
      <p className="meta">NO PASSWORD — PICK WHO YOU ARE</p>

      <section className="panel">
        <ErrorMessage message={users.error} />
        <form className="stacked" onSubmit={handleLogIn}>
          <label htmlFor="login-user">User</label>
          <select id="login-user" value={selectedUserId} onChange={handleUserChange} required>
            <option value="" disabled>
              Choose a user…
            </option>
            {users.data?.map(renderUserOption)}
          </select>
          <button type="submit">Log in</button>
        </form>
      </section>

      <section className="panel">
        <h2>New user</h2>
        <form className="stacked" onSubmit={handleCreateUser}>
          <label htmlFor="new-user-name">Name</label>
          <input id="new-user-name" value={newUserName} onChange={handleNameChange} required />
          <button type="submit">Create and log in</button>
        </form>
        <ErrorMessage message={creation.error} />
      </section>
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
