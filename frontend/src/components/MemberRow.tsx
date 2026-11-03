import type { ReactElement } from 'react'
import type { Member } from '../types/api'

interface MemberRowProps {
  member: Member
  name: string
  /** Present only when the caller is the group admin. */
  onRemove?(userId: number): void
}

export function MemberRow({ member, name, onRemove }: MemberRowProps): ReactElement {
  function handleRemoveClick(): void {
    onRemove?.(member.user_id)
  }

  return (
    <li>
      {name}
      {member.role === 'admin' && ' (admin)'}
      {onRemove !== undefined && member.role !== 'admin' && (
        <button type="button" className="link-button" onClick={handleRemoveClick}>
          Remove {name}
        </button>
      )}
    </li>
  )
}
