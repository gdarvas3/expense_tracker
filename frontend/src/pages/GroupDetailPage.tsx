import { useCallback, type ReactElement } from 'react'
import { Link, useParams } from 'react-router'
import {
  addMember,
  createExpense,
  getBalances,
  getGroup,
  getSettlementPlan,
  listExpenses,
  listUsers,
  recordSettlement,
  removeMember,
} from '../api/endpoints'
import { AddMemberForm } from '../components/AddMemberForm'
import { BalanceList } from '../components/BalanceList'
import { ErrorMessage } from '../components/ErrorMessage'
import { ExpenseForm } from '../components/ExpenseForm'
import { ExpenseList } from '../components/ExpenseList'
import { MemberList } from '../components/MemberList'
import { SettlementForm } from '../components/SettlementForm'
import { SettlementPlan } from '../components/SettlementPlan'
import { useLoggedInUser } from '../context/currentUser'
import { useApiData } from '../hooks/useApiData'
import type {
  Balance,
  Expense,
  ExpenseInput,
  Group,
  Member,
  SettlementInput,
  Transfer,
  User,
} from '../types/api'

export function GroupDetailPage(): ReactElement {
  const user = useLoggedInUser()
  const groupId = Number(useParams().groupId)
  const loadGroup = useCallback(
    function loadGroup(): Promise<Group> {
      return getGroup(user.id, groupId)
    },
    [user.id, groupId],
  )
  const loadExpenses = useCallback(
    function loadExpenses(): Promise<Expense[]> {
      return listExpenses(user.id, groupId)
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
  const expenses = useApiData(loadExpenses)
  const balances = useApiData(loadBalances)
  const plan = useApiData(loadPlan)

  // Any change can move every balance, so everything derived from them is fetched again.
  function reloadGroupData(): void {
    group.reload()
    expenses.reload()
    balances.reload()
    plan.reload()
  }

  async function handleAddExpense(expense: ExpenseInput): Promise<void> {
    await createExpense(user.id, groupId, expense)
    reloadGroupData()
  }

  async function handleRecordSettlement(settlement: SettlementInput): Promise<void> {
    await recordSettlement(user.id, groupId, settlement)
    reloadGroupData()
  }

  async function handleAddMember(memberId: number): Promise<void> {
    await addMember(user.id, groupId, memberId)
    reloadGroupData()
  }

  async function handleRemoveMember(memberId: number): Promise<void> {
    await removeMember(user.id, groupId, memberId)
    reloadGroupData()
  }

  function isCurrentUserAdmin(member: Member): boolean {
    return member.user_id === user.id && member.role === 'admin'
  }

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

  const members = group.data.members
  const memberIds = members.map(toUserId)
  const isAdmin = members.some(isCurrentUserAdmin)
  const userNames = toNameMap(users.data ?? [])
  const candidateIds = (users.data ?? []).map(toId).filter(isNotIn(memberIds))
  // Remount the forms when membership changes, so their participant lists start fresh.
  const membershipKey = memberIds.join(',')

  return (
    <>
      <Link to="/" className="back-link">
        ← My groups
      </Link>
      <div className="page-title">
        <h1>{group.data.name}</h1>
        <p className="meta">GROUP #{group.data.id} · {members.length} MEMBERS</p>
      </div>

      <div className="group-layout">
        {/* Decorative receipt framing; the table inside stays a plain, accessible table. */}
        <section className="receipt" aria-labelledby="expenses-heading">
          <p className="receipt-banner" aria-hidden="true">
            *** SHARED EXPENSES ***
          </p>
          <h2 id="expenses-heading">Expenses</h2>
          <ErrorMessage message={expenses.error} />
          {expenses.data && <ExpenseList expenses={expenses.data} userNames={userNames} />}
          <div className="receipt-footer" aria-hidden="true">
            <div className="barcode" />
            THANK YOU FOR SPLITTING FAIRLY
          </div>
        </section>

        <div className="group-side">
          <section className="panel">
            <h2>Balances</h2>
            <ErrorMessage message={balances.error} />
            {balances.data && <BalanceList balances={balances.data} userNames={userNames} />}
          </section>

          <section>
            <h2>Settlement plan</h2>
            <ErrorMessage message={plan.error} />
            {plan.data && <SettlementPlan transfers={plan.data} userNames={userNames} />}
          </section>

          <section className="panel">
            <h2>Add an expense</h2>
            <ExpenseForm
              key={membershipKey}
              members={members}
              userNames={userNames}
              defaultPayerId={user.id}
              onSubmit={handleAddExpense}
            />
          </section>

          <section className="panel">
            <h2>Record a payment</h2>
            <SettlementForm
              key={membershipKey}
              members={members}
              userNames={userNames}
              defaultPayerId={user.id}
              onSubmit={handleRecordSettlement}
            />
          </section>

          <section className="panel">
            <h2>Members</h2>
            <MemberList
              members={members}
              userNames={userNames}
              onRemove={isAdmin ? handleRemoveMember : undefined}
            />
            {isAdmin && (
              <AddMemberForm
                candidateIds={candidateIds}
                userNames={userNames}
                onAdd={handleAddMember}
              />
            )}
          </section>
        </div>
      </div>
    </>
  )
}

function toNameMap(users: User[]): Map<number, string> {
  return new Map(users.map(toNameEntry))
}

function toNameEntry(user: User): [number, string] {
  return [user.id, user.name]
}

function toId(user: User): number {
  return user.id
}

function toUserId(member: Member): number {
  return member.user_id
}

function isNotIn(excludedIds: number[]): (userId: number) => boolean {
  return function isNotExcluded(userId: number): boolean {
    return !excludedIds.includes(userId)
  }
}
