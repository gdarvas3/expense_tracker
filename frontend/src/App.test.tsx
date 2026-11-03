import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { storeUser } from './context/userStorage'
import { ALICE, BOB, GROUP } from './test/fixtures'
import { renderApp } from './test/renderApp'

describe('App', function appSuite() {
  it('redirects to the login page when nobody is logged in', async function redirectsToTheLoginPageWhenNobodyIsLoggedIn() {
    renderApp('/', { 'GET /api/users': { body: [ALICE, BOB] } })

    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
  })

  it('logs in as the chosen user and shows their groups', async function logsInAsTheChosenUserAndShowsTheirGroups() {
    renderApp('/', {
      'GET /api/users': { body: [ALICE, BOB] },
      'GET /api/groups': { body: [GROUP] },
    })
    const user = userEvent.setup()

    await user.selectOptions(await screen.findByLabelText('User'), 'Bob')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('link', { name: 'Flat 4B' })).toBeInTheDocument()
    expect(screen.getByText('Logged in as Bob')).toBeInTheDocument()
  })

  it('shows the group members, balances and settlement plan', async function showsTheGroupMembersBalancesAndSettlementPlan() {
    storeUser(ALICE)
    renderApp('/groups/10', {
      'GET /api/users': { body: [ALICE, BOB] },
      'GET /api/groups/10': { body: GROUP },
      'GET /api/groups/10/expenses': { body: [] },
      'GET /api/groups/10/balances': {
        body: [
          { user_id: 1, net: '40.00' },
          { user_id: 2, net: '-40.00' },
        ],
      },
      'GET /api/groups/10/settlement-plan': {
        body: [{ from_user_id: 2, to_user_id: 1, amount: '40.00' }],
      },
    })

    expect(await screen.findByRole('heading', { name: 'Flat 4B' })).toBeInTheDocument()
    expect(await screen.findByText('Bob pays Alice 40.00')).toBeInTheDocument()
    expect(screen.getByText('-40.00')).toBeInTheDocument()
  })

  it('shows the backend message when a non-member opens a group (AC-7)', async function showsTheBackendMessageWhenANonMemberOpensAGroupAc7() {
    storeUser(BOB)
    renderApp('/groups/10', {
      'GET /api/users': { body: [ALICE, BOB] },
      'GET /api/groups/10': {
        status: 403,
        body: { detail: 'You are not a member of this group.' },
      },
    })

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'You are not a member of this group.',
    )
  })
})
