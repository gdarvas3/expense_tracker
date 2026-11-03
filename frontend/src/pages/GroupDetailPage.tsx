import { useCallback, type ReactElement } from 'react'
import { Link, useParams } from 'react-router'
import { getBalances, getGroup, getSettlementPlan, listUsers } from '../api/endpoints'
import { BalanceList } from '../components/BalanceList'
import { ErrorMessage } from '../components/ErrorMessage'
import { MemberList } from '../components/MemberList'
import { SettlementPlan } from '../components/SettlementPlan'
import { useLoggedInUser } from '../context/currentUser'
import { useApiData } from '../hooks/useApiData'
import type { Balance, Group, Transfer, User } from '../types/api'

export function GroupDetailPage(): ReactElement {
  const user = useLoggedInUser()
  const groupId = Number(useParams().groupId)
  const loadGroup = useCallback(
    function loadGroup(): Promise<Group> {
      return getGroup(user.id, groupId)
    },
    [user.id, groupId],
  )
  const loadBalances = useCallback(
    function loadBalances(): Promise<Balance[]> {
      return getBalances(user.id, groupId)
    },
    [user.id, groupId],
  )
  const loadPlan = useCallback(
    function loadPlan(): Promise<Transfer[]> {
      return getSettlementPlan(user.id, groupId)
    },
    [user.id, groupId],
  )
  const group = useApiData(loadGroup)
  const users = useApiData(listUsers)
  const balances = useApiData(loadBalances)
  const plan = useApiData(loadPlan)

  // A non-member gets 403 on every group endpoint; showing the first message is enough (AC-7).
  if (group.error !== null) {
    return (
      <>
        <ErrorMessage message={group.error} />
        <Link to="/">Back to my groups</Link>
      </>
    )
  }
  if (group.data === null) {
    return <p>Loading…</p>
  }

  const userNames = toNameMap(users.data ?? [])
  return (
    <>
      <Link to="/">← My groups</Link>
      <h1>{group.data.name}</h1>

      <h2>Members</h2>
      <MemberList members={group.data.members} userNames={userNames} />

      <h2>Balances</h2>
      <ErrorMessage message={balances.error} />
      {balances.data && <BalanceList balances={balances.data} userNames={userNames} />}

      <h2>Settlement plan</h2>
      <ErrorMessage message={plan.error} />
      {plan.data && <SettlementPlan transfers={plan.data} userNames={userNames} />}
    </>
  )
}

function toNameMap(users: User[]): Map<number, string> {
  return new Map(users.map(toNameEntry))
}

function toNameEntry(user: User): [number, string] {
  return [user.id, user.name]
}
