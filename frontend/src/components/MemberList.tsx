import type { ReactElement } from 'react'
import { useAsyncAction } from '../hooks/useAsyncAction'
import type { Member } from '../types/api'
import { ErrorMessage } from './ErrorMessage'
import { MemberRow } from './MemberRow'

interface MemberListProps {
  members: Member[]
  userNames: Map<number, string>
  /** Present only when the caller is the group admin. */
  onRemove?(userId: number): Promise<void>
}

export function MemberList({ members, userNames, onRemove }: MemberListProps): ReactElement {
  const removal = useAsyncAction(removeMember)

  async function removeMember(userId: number): Promise<void> {
    await onRemove?.(userId)
  }

  function startRemoval(userId: number): void {
    void removal.run(userId)
  }

  function renderMember(member: Member): ReactElement {
    return (
      <MemberRow
        key={member.user_id}
        member={member}
        name={userNames.get(member.user_id) ?? `User ${member.user_id}`}
        onRemove={onRemove === undefined ? undefined : startRemoval}
      />
    )
  }

  return (
    <>
      <ul className="member-list">{members.map(renderMember)}</ul>
      {/* AC-6: the backend refuses (409) to remove a member whose balance is not zero. */}
      <ErrorMessage message={removal.error} />
    </>
  )
}
