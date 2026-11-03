import type { ReactElement } from 'react'
import type { Member } from '../types/api'

interface MemberListProps {
  members: Member[]
  userNames: Map<number, string>
}

export function MemberList({ members, userNames }: MemberListProps): ReactElement {
  function renderMember(member: Member): ReactElement {
    return (
      <li key={member.user_id}>
        {userNames.get(member.user_id) ?? `User ${member.user_id}`}
        {member.role === 'admin' && ' (admin)'}
      </li>
    )
  }

  return <ul>{members.map(renderMember)}</ul>
}
