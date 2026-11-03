import { useState, type FormEvent, type ReactElement } from 'react'
import { useAsyncAction } from '../hooks/useAsyncAction'
import { ErrorMessage } from './ErrorMessage'
import { MemberSelect } from './MemberSelect'

interface AddMemberFormProps {
  /** Users who are not members of the group yet. */
  candidateIds: number[]
  userNames: Map<number, string>
  onAdd(userId: number): Promise<void>
}

export function AddMemberForm(props: AddMemberFormProps): ReactElement {
  const [userId, setUserId] = useState('')
  const adding = useAsyncAction(props.onAdd)

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    if (await adding.run(Number(userId))) {
      setUserId('')
    }
  }

  if (props.candidateIds.length === 0) {
    return <p>Every user is already a member.</p>
  }
  return (
    <form aria-label="Add member" onSubmit={handleSubmit}>
      <label htmlFor="new-member">User</label>
      <MemberSelect
        id="new-member"
        userIds={props.candidateIds}
        userNames={props.userNames}
        value={userId}
        onChange={setUserId}
        placeholder="Choose…"
      />
      <button type="submit" disabled={adding.isRunning}>
        Add member
      </button>
      <ErrorMessage message={adding.error} />
    </form>
  )
}
