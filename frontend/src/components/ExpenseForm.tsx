import { useState, type ChangeEvent, type FormEvent, type ReactElement } from 'react'
import { useAsyncAction } from '../hooks/useAsyncAction'
import type { ExpenseInput, Member, ParticipantInput, SplitType } from '../types/api'
import { ErrorMessage } from './ErrorMessage'
import { MemberSelect } from './MemberSelect'
import { ParticipantRow } from './ParticipantRow'

interface ExpenseFormProps {
  members: Member[]
  userNames: Map<number, string>
  defaultPayerId: number
  onSubmit(expense: ExpenseInput): Promise<void>
}

interface ParticipantDraft {
  isIncluded: boolean
  value: string
}

/** Which participant field each split type needs; null means none (equal split). */
const VALUE_FIELD_BY_SPLIT_TYPE: Record<SplitType, 'percentage' | 'amount' | null> = {
  equal: null,
  percentage: 'percentage',
  exact: 'amount',
}

/**
 * Form for a new expense. It only collects input; the backend validates the split
 * (percentages sum to 100%, exact amounts sum to the total) and its message is shown (AC-5).
 */
export function ExpenseForm(props: ExpenseFormProps): ReactElement {
  const memberIds = props.members.map(toUserId)
  const [description, setDescription] = useState('')
  const [amount, setAmount] = useState('')
  const [payerId, setPayerId] = useState(String(props.defaultPayerId))
  const [splitType, setSplitType] = useState<SplitType>('equal')
  const [drafts, setDrafts] = useState(function initialDrafts() {
    return createDrafts(memberIds)
  })
  const submission = useAsyncAction(props.onSubmit)
  const valueField = VALUE_FIELD_BY_SPLIT_TYPE[splitType]

  function handleDescriptionChange(event: ChangeEvent<HTMLInputElement>): void {
    setDescription(event.target.value)
  }

  function handleAmountChange(event: ChangeEvent<HTMLInputElement>): void {
    setAmount(event.target.value)
  }

  function handleSplitTypeChange(event: ChangeEvent<HTMLSelectElement>): void {
    setSplitType(event.target.value as SplitType)
  }

  function updateDraft(userId: number, change: Partial<ParticipantDraft>): void {
    setDrafts(new Map(drafts).set(userId, { ...draftOf(userId), ...change }))
  }

  function handleIncludedChange(userId: number, isIncluded: boolean): void {
    updateDraft(userId, { isIncluded })
  }

  function handleValueChange(userId: number, value: string): void {
    updateDraft(userId, { value })
  }

  function draftOf(userId: number): ParticipantDraft {
    return drafts.get(userId) ?? { isIncluded: true, value: '' }
  }

  function isIncluded(userId: number): boolean {
    return draftOf(userId).isIncluded
  }

  function toParticipant(userId: number): ParticipantInput {
    return valueField === null ? { user_id: userId } : { user_id: userId, [valueField]: draftOf(userId).value }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    const succeeded = await submission.run({
      description: description.trim(),
      amount,
      payer_id: Number(payerId),
      split_type: splitType,
      participants: memberIds.filter(isIncluded).map(toParticipant),
    })
    if (succeeded) {
      setDescription('')
      setAmount('')
      setDrafts(createDrafts(memberIds))
    }
  }

  function renderParticipant(userId: number): ReactElement {
    const draft = draftOf(userId)
    return (
      <ParticipantRow
        key={userId}
        userId={userId}
        name={props.userNames.get(userId) ?? `User ${userId}`}
        isIncluded={draft.isIncluded}
        value={draft.value}
        valueLabel={valueField}
        onIncludedChange={handleIncludedChange}
        onValueChange={handleValueChange}
      />
    )
  }

  return (
    <form aria-label="New expense" className="stacked" onSubmit={handleSubmit}>
      <label htmlFor="expense-description">Description</label>
      <input
        id="expense-description"
        value={description}
        onChange={handleDescriptionChange}
        required
      />

      <label htmlFor="expense-amount">Amount</label>
      <input
        id="expense-amount"
        inputMode="decimal"
        placeholder="0.00"
        value={amount}
        onChange={handleAmountChange}
        required
      />

      <label htmlFor="expense-payer">Paid by</label>
      <MemberSelect
        id="expense-payer"
        userIds={memberIds}
        userNames={props.userNames}
        value={payerId}
        onChange={setPayerId}
      />

      <label htmlFor="expense-split">Split</label>
      <select id="expense-split" value={splitType} onChange={handleSplitTypeChange}>
        <option value="equal">Equally</option>
        <option value="percentage">By percentage</option>
        <option value="exact">By exact amounts</option>
      </select>

      <fieldset>
        <legend>Shared by</legend>
        <ul className="participants">{memberIds.map(renderParticipant)}</ul>
      </fieldset>

      <button type="submit" disabled={submission.isRunning}>
        Add expense
      </button>
      <ErrorMessage message={submission.error} />
    </form>
  )
}

function createDrafts(userIds: number[]): Map<number, ParticipantDraft> {
  return new Map(userIds.map(toEmptyDraft))
}

function toEmptyDraft(userId: number): [number, ParticipantDraft] {
  return [userId, { isIncluded: true, value: '' }]
}

function toUserId(member: Member): number {
  return member.user_id
}
