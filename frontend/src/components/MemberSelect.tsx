import type { ChangeEvent, ReactElement } from 'react'

interface MemberSelectProps {
  id: string
  userIds: number[]
  userNames: Map<number, string>
  value: string
  onChange(value: string): void
  /** Shown as a disabled first option when nobody is chosen yet. */
  placeholder?: string
}

/** A <select> of users by name; the value is the user ID as a string. */
export function MemberSelect(props: MemberSelectProps): ReactElement {
  function handleChange(event: ChangeEvent<HTMLSelectElement>): void {
    props.onChange(event.target.value)
  }

  function renderOption(userId: number): ReactElement {
    return (
      <option key={userId} value={userId}>
        {props.userNames.get(userId) ?? `User ${userId}`}
      </option>
    )
  }

  return (
    <select id={props.id} value={props.value} onChange={handleChange} required>
      {props.placeholder !== undefined && (
        <option value="" disabled>
          {props.placeholder}
        </option>
      )}
      {props.userIds.map(renderOption)}
    </select>
  )
}
