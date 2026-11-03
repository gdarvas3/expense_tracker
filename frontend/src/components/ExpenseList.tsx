import type { ReactElement } from 'react'
import type { Expense, SplitType } from '../types/api'

interface ExpenseListProps {
  expenses: Expense[]
  userNames: Map<number, string>
}

const SPLIT_TYPE_LABELS: Record<SplitType, string> = {
  equal: 'Equally',
  percentage: 'By percentage',
  exact: 'By exact amounts',
}

export function ExpenseList({ expenses, userNames }: ExpenseListProps): ReactElement {
  function renderExpense(expense: Expense): ReactElement {
    return (
      <tr key={expense.id}>
        <td>{expense.description}</td>
        <td>{userNames.get(expense.payer_id) ?? `User ${expense.payer_id}`}</td>
        <td>{SPLIT_TYPE_LABELS[expense.split_type]}</td>
        <td className="amount">{expense.amount}</td>
      </tr>
    )
  }

  if (expenses.length === 0) {
    return <p>No expenses yet.</p>
  }
  return (
    <table aria-label="Expenses">
      <thead>
        <tr>
          <th>Description</th>
          <th>Paid by</th>
          <th>Split</th>
          <th className="amount">Amount</th>
        </tr>
      </thead>
      <tbody>{expenses.map(renderExpense)}</tbody>
    </table>
  )
}
