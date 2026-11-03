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
        <td className={balance.net.startsWith('-') ? 'amount negative' : 'amount'}>
          {balance.net}
        </td>
      </tr>
    )
  }

  return (
    <table>
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
