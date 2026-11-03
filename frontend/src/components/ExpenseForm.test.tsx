import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client'
import { MEMBERS, USER_NAMES } from '../test/fixtures'
import type { ExpenseInput } from '../types/api'
import { ExpenseForm } from './ExpenseForm'

function renderForm(submit: (expense: ExpenseInput) => Promise<void>): void {
  render(
    <ExpenseForm members={MEMBERS} userNames={USER_NAMES} defaultPayerId={1} onSubmit={submit} />,
  )
}

async function acceptExpense(): Promise<void> {}

describe('ExpenseForm', function expenseFormSuite() {
  it('submits an equal split among all members by default', async function submitsEqualSplit() {
    const submit = vi.fn(acceptExpense)
    renderForm(submit)
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('Description'), 'Groceries')
    await user.type(screen.getByLabelText('Amount'), '90.00')
    await user.click(screen.getByRole('button', { name: 'Add expense' }))

    expect(submit).toHaveBeenCalledWith({
      description: 'Groceries',
      amount: '90.00',
      payer_id: 1,
      split_type: 'equal',
      participants: [{ user_id: 1 }, { user_id: 2 }],
    })
    expect(screen.getByLabelText('Description')).toHaveValue('')
  })

  it('submits a percentage per participant', async function submitsPercentages() {
    const submit = vi.fn(acceptExpense)
    renderForm(submit)
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('Description'), 'Internet')
    await user.type(screen.getByLabelText('Amount'), '30.00')
    await user.selectOptions(screen.getByLabelText('Paid by'), 'Bob')
    await user.selectOptions(screen.getByLabelText('Split'), 'percentage')
    await user.type(screen.getByLabelText('Alice percentage'), '60')
    await user.type(screen.getByLabelText('Bob percentage'), '40')
    await user.click(screen.getByRole('button', { name: 'Add expense' }))

    expect(submit).toHaveBeenCalledWith({
      description: 'Internet',
      amount: '30.00',
      payer_id: 2,
      split_type: 'percentage',
      participants: [
        { user_id: 1, percentage: '60' },
        { user_id: 2, percentage: '40' },
      ],
    })
  })

  it('leaves out unticked members in an exact split', async function leavesOutUntickedMembers() {
    const submit = vi.fn(acceptExpense)
    renderForm(submit)
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('Description'), 'Taxi')
    await user.type(screen.getByLabelText('Amount'), '25.00')
    await user.selectOptions(screen.getByLabelText('Split'), 'exact')
    await user.click(screen.getByRole('checkbox', { name: 'Bob' }))
    await user.type(screen.getByLabelText('Alice amount'), '25.00')
    await user.click(screen.getByRole('button', { name: 'Add expense' }))

    expect(submit).toHaveBeenCalledWith(
      expect.objectContaining({
        split_type: 'exact',
        participants: [{ user_id: 1, amount: '25.00' }],
      }),
    )
  })

  it('shows the backend error and keeps the input (AC-5)', async function showsBackendError() {
    async function rejectExpense(): Promise<void> {
      throw new ApiError(400, 'Percentages must add up to exactly 100%.')
    }
    renderForm(vi.fn(rejectExpense))
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('Description'), 'Internet')
    await user.type(screen.getByLabelText('Amount'), '30.00')
    await user.click(screen.getByRole('button', { name: 'Add expense' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Percentages must add up to exactly 100%.',
    )
    expect(screen.getByLabelText('Description')).toHaveValue('Internet')
  })
})
