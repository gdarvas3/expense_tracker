import type { ReactElement } from 'react'
import type { Balance } from '../types/api'

interface BalanceListProps {
  balances: Balance[]
  userNames: Map<number, string>
}

/** Net balance per member: positive means the others owe them. */
export function BalanceList({ balances, userNames }: BalanceListProps): ReactElement {
  function renderBalance(balance: Balance): ReactElement {
    return (
      <tr key={balance.user_id}>
        <td>{userNames.get(balance.user_id) ?? `User ${balance.user_id}`}</td>
        <td className={`amount ${signClassOf(balance.net)}`}>{balance.net}</td>
      </tr>
    )
  }

  return (
    <table aria-label="Balances">
      <thead>
        <tr>
          <th>Member</th>
          <th className="amount">Net balance</th>
        </tr>
      </thead>
      <tbody>{balances.map(renderBalance)}</tbody>
    </table>
  )
}

/** Matches "0", "0.00" or "-0.00": a settled member gets no colour. */
const ZERO_AMOUNT = /^-?0+(\.0+)?$/

/** Colour class for a decimal string; no money arithmetic, only its sign. */
function signClassOf(amount: string): string {
  if (ZERO_AMOUNT.test(amount)) {
    return ''
  }
  return amount.startsWith('-') ? 'negative' : 'positive'
}
