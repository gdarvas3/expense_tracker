import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { storeUser } from '../context/userStorage'
import type { MockRoutes } from '../test/fetchMock'
import { ALICE, BOB, CAROL, GROCERIES, GROUP } from '../test/fixtures'
import { countCalls, renderApp } from '../test/renderApp'

const GROUP_ROUTES: MockRoutes = {
  'GET /api/users': { body: [ALICE, BOB, CAROL] },
  'GET /api/groups/10': { body: GROUP },
  'GET /api/groups/10/expenses': { body: [GROCERIES] },
  'GET /api/groups/10/balances': {
    body: [
      { user_id: 1, net: '40.00' },
      { user_id: 2, net: '-40.00' },
    ],
  },
  'GET /api/groups/10/settlement-plan': {
    body: [{ from_user_id: 2, to_user_id: 1, amount: '40.00' }],
  },
}

describe('GroupDetailPage', function groupDetailPageSuite() {
  it('lists the expenses of the group', async function listsExpenses() {
    storeUser(ALICE)
    renderApp('/groups/10', GROUP_ROUTES)

    const expenseTable = await screen.findByRole('table', { name: 'Expenses' })
    expect(within(expenseTable).getByText('Groceries')).toBeInTheDocument()
    expect(within(expenseTable).getByText('80.00')).toBeInTheDocument()
  })

  it('records an expense and reloads the balances', async function recordsExpense() {
    storeUser(ALICE)
    const fetchStub = renderApp('/groups/10', {
      ...GROUP_ROUTES,
      'POST /api/groups/10/expenses': { status: 201, body: GROCERIES },
    })
    const user = userEvent.setup()
    const expenseForm = await screen.findByRole('form', { name: 'New expense' })

    await user.type(within(expenseForm).getByLabelText('Description'), 'Groceries')
    await user.type(within(expenseForm).getByLabelText('Amount'), '80.00')
    await user.click(within(expenseForm).getByRole('button', { name: 'Add expense' }))

    expect(countCalls(fetchStub, 'POST /api/groups/10/expenses')).toBe(1)
    expect(countCalls(fetchStub, 'GET /api/groups/10/balances')).toBe(2)
  })

  it('records a settlement and reloads the plan (AC-8)', async function recordsSettlement() {
    storeUser(BOB)
    const fetchStub = renderApp('/groups/10', {
      ...GROUP_ROUTES,
      'POST /api/groups/10/settlements': {
        status: 201,
        body: { id: 1, payer_id: 2, payee_id: 1, amount: '40.00', created_at: '' },
      },
    })
    const user = userEvent.setup()
    const settlementForm = await screen.findByRole('form', { name: 'Record a payment' })

    await user.selectOptions(within(settlementForm).getByLabelText('To'), 'Alice')
    await user.type(within(settlementForm).getByLabelText('Amount'), '40.00')
    await user.click(within(settlementForm).getByRole('button', { name: 'Record payment' }))

    expect(countCalls(fetchStub, 'POST /api/groups/10/settlements')).toBe(1)
    expect(countCalls(fetchStub, 'GET /api/groups/10/settlement-plan')).toBe(2)
  })

  it('lets the admin add a member who is not in the group yet', async function addsMember() {
    storeUser(ALICE)
    const fetchStub = renderApp('/groups/10', {
      ...GROUP_ROUTES,
      'POST /api/groups/10/members': { status: 201, body: { user_id: 3, role: 'member' } },
    })
    const user = userEvent.setup()
    const memberForm = await screen.findByRole('form', { name: 'Add member' })

    await user.selectOptions(within(memberForm).getByLabelText('User'), 'Carol')
    await user.click(within(memberForm).getByRole('button', { name: 'Add member' }))

    expect(countCalls(fetchStub, 'POST /api/groups/10/members')).toBe(1)
  })

  it('shows why a member with a balance cannot be removed (AC-6)', async function showsRemovalConflict() {
    storeUser(ALICE)
    renderApp('/groups/10', {
      ...GROUP_ROUTES,
      'DELETE /api/groups/10/members/2': {
        status: 409,
        body: { detail: 'Only members with a zero balance can be removed.' },
      },
    })
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: 'Remove Bob' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Only members with a zero balance can be removed.',
    )
  })

  it('hides member management from regular members', async function hidesMemberManagement() {
    storeUser(BOB)
    renderApp('/groups/10', GROUP_ROUTES)

    expect(await screen.findByRole('heading', { name: 'Flat 4B' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Remove Alice' })).not.toBeInTheDocument()
    expect(screen.queryByRole('form', { name: 'Add member' })).not.toBeInTheDocument()
  })
})
