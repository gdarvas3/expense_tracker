import type { ChangeEvent, ReactElement } from 'react'

interface ParticipantRowProps {
  userId: number
  name: string
  isIncluded: boolean
  value: string
  /** "percentage" or "amount"; null when the split type needs no value (equal split). */
  valueLabel: string | null
  onIncludedChange(userId: number, isIncluded: boolean): void
  onValueChange(userId: number, value: string): void
}

/** One member in the expense form: whether they share the expense, and their part of it. */
export function ParticipantRow(props: ParticipantRowProps): ReactElement {
  function handleIncludedChange(event: ChangeEvent<HTMLInputElement>): void {
    props.onIncludedChange(props.userId, event.target.checked)
  }

  function handleValueChange(event: ChangeEvent<HTMLInputElement>): void {
    props.onValueChange(props.userId, event.target.value)
  }

  return (
    <li className="participant">
      <label>
        <input type="checkbox" checked={props.isIncluded} onChange={handleIncludedChange} />
        {props.name}
      </label>
      {props.valueLabel !== null && (
        <input
          aria-label={`${props.name} ${props.valueLabel}`}
          inputMode="decimal"
          value={props.value}
          onChange={handleValueChange}
          disabled={!props.isIncluded}
          required={props.isIncluded}
        />
      )}
    </li>
  )
}
