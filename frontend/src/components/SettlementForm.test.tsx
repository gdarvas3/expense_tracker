import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client'
import { MEMBERS, USER_NAMES } from '../test/fixtures'
import type { SettlementInput } from '../types/api'
import { SettlementForm } from './SettlementForm'

function renderForm(submit: (settlement: SettlementInput) => Promise<void>): void {
  render(
    <SettlementForm
      members={MEMBERS}
      userNames={USER_NAMES}
      defaultPayerId={2}
      onSubmit={submit}
    />,
  )
}

async function acceptSettlement(): Promise<void> {}

describe('SettlementForm', function settlementFormSuite() {
  it('submits a payment from the caller to the chosen member (AC-8)', async function submitsPayment() {
    const submit = vi.fn(acceptSettlement)
    renderForm(submit)
    const user = userEvent.setup()

    await user.selectOptions(screen.getByLabelText('To'), 'Alice')
    await user.type(screen.getByLabelText('Amount'), '40.00')
    await user.click(screen.getByRole('button', { name: 'Record payment' }))

    expect(submit).toHaveBeenCalledWith({ payer_id: 2, payee_id: 1, amount: '40.00' })
    expect(screen.getByLabelText('Amount')).toHaveValue('')
  })

  it('shows the backend error', async function showsBackendError() {
    async function rejectSettlement(): Promise<void> {
      throw new ApiError(400, 'Payer and payee must be different members.')
    }
    renderForm(vi.fn(rejectSettlement))
    const user = userEvent.setup()

    await user.selectOptions(screen.getByLabelText('To'), 'Bob')
    await user.type(screen.getByLabelText('Amount'), '5.00')
    await user.click(screen.getByRole('button', { name: 'Record payment' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Payer and payee must be different members.',
    )
  })
})
