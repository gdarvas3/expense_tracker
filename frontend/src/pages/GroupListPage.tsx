import { useCallback, useState, type ChangeEvent, type FormEvent, type ReactElement } from 'react'
import { Link } from 'react-router'
import { describeError } from '../api/client'
import { createGroup, listGroups } from '../api/endpoints'
import { ErrorMessage } from '../components/ErrorMessage'
import { useLoggedInUser } from '../context/currentUser'
import { useApiData } from '../hooks/useApiData'
import type { Group } from '../types/api'

export function GroupListPage(): ReactElement {
  const user = useLoggedInUser()
  const loadGroups = useCallback(
    function loadGroups(): Promise<Group[]> {
      return listGroups(user.id)
    },
    [user.id],
  )
  const groups = useApiData(loadGroups)
  const [newGroupName, setNewGroupName] = useState('')
  const [createError, setCreateError] = useState<string | null>(null)

  function handleNameChange(event: ChangeEvent<HTMLInputElement>): void {
    setNewGroupName(event.target.value)
  }

  async function handleCreateGroup(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    try {
      await createGroup(user.id, newGroupName.trim())
      setNewGroupName('')
      setCreateError(null)
      groups.reload()
    } catch (error) {
      setCreateError(describeError(error))
    }
  }

  return (
    <>
      <h1>My groups</h1>
      <ErrorMessage message={groups.error} />
      {groups.data?.length === 0 && <p>You are not a member of any group yet.</p>}
      <ul>{groups.data?.map(renderGroupLink)}</ul>

      <h2>New group</h2>
      <form onSubmit={handleCreateGroup}>
        <label htmlFor="new-group-name">Name</label>
        <input id="new-group-name" value={newGroupName} onChange={handleNameChange} required />
        <button type="submit">Create group</button>
      </form>
      <ErrorMessage message={createError} />
    </>
  )
}

function renderGroupLink(group: Group): ReactElement {
  return (
    <li key={group.id}>
      <Link to={`/groups/${group.id}`}>{group.name}</Link>
    </li>
  )
}
