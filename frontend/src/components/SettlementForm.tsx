import { useState, type ChangeEvent, type FormEvent, type ReactElement } from 'react'
import { useAsyncAction } from '../hooks/useAsyncAction'
import type { Member, SettlementInput } from '../types/api'
import { ErrorMessage } from './ErrorMessage'
import { MemberSelect } from './MemberSelect'

interface SettlementFormProps {
  members: Member[]
  userNames: Map<number, string>
  defaultPayerId: number
  onSubmit(settlement: SettlementInput): Promise<void>
}

/** Records a direct payment between two members, which reduces their debt (AC-8). */
export function SettlementForm(props: SettlementFormProps): ReactElement {
  const memberIds = props.members.map(toUserId)
  const [payerId, setPayerId] = useState(String(props.defaultPayerId))
  const [payeeId, setPayeeId] = useState('')
  const [amount, setAmount] = useState('')
  const submission = useAsyncAction(props.onSubmit)

  function handleAmountChange(event: ChangeEvent<HTMLInputElement>): void {
    setAmount(event.target.value)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    const succeeded = await submission.run({
      payer_id: Number(payerId),
      payee_id: Number(payeeId),
      amount,
    })
    if (succeeded) {
      setPayeeId('')
      setAmount('')
    }
  }

  return (
    <form aria-label="Record a payment" onSubmit={handleSubmit}>
      <label htmlFor="settlement-payer">From</label>
      <MemberSelect
        id="settlement-payer"
        userIds={memberIds}
        userNames={props.userNames}
        value={payerId}
        onChange={setPayerId}
      />

      <label htmlFor="settlement-payee">To</label>
      <MemberSelect
        id="settlement-payee"
        userIds={memberIds}
        userNames={props.userNames}
        value={payeeId}
        onChange={setPayeeId}
        placeholder="Choose…"
      />

      <label htmlFor="settlement-amount">Amount</label>
      <input
        id="settlement-amount"
        inputMode="decimal"
        placeholder="0.00"
        value={amount}
        onChange={handleAmountChange}
        required
      />

      <button type="submit" disabled={submission.isRunning}>
        Record payment
      </button>
      <ErrorMessage message={submission.error} />
    </form>
  )
}

function toUserId(member: Member): number {
  return member.user_id
}
