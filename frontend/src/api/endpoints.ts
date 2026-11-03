/** One typed function per backend endpoint; userId is the caller (sent as X-User-Id). */

import type {
  Balance,
  Expense,
  ExpenseInput,
  Group,
  Member,
  Settlement,
  SettlementInput,
  Transfer,
  User,
} from '../types/api'
import { apiRequest } from './client'

export function listUsers(): Promise<User[]> {
  return apiRequest({ method: 'GET', path: '/users' })
}

export function createUser(name: string): Promise<User> {
  return apiRequest({ method: 'POST', path: '/users', body: { name } })
}

export function listGroups(userId: number): Promise<Group[]> {
  return apiRequest({ method: 'GET', path: '/groups', userId })
}

export function createGroup(userId: number, name: string): Promise<Group> {
  return apiRequest({ method: 'POST', path: '/groups', userId, body: { name } })
}

export function getGroup(userId: number, groupId: number): Promise<Group> {
  return apiRequest({ method: 'GET', path: `/groups/${groupId}`, userId })
}

export function addMember(userId: number, groupId: number, memberId: number): Promise<Member> {
  return apiRequest({
    method: 'POST',
    path: `/groups/${groupId}/members`,
    userId,
    body: { user_id: memberId },
  })
}

export function removeMember(userId: number, groupId: number, memberId: number): Promise<void> {
  return apiRequest({ method: 'DELETE', path: `/groups/${groupId}/members/${memberId}`, userId })
}

export function listExpenses(userId: number, groupId: number): Promise<Expense[]> {
  return apiRequest({ method: 'GET', path: `/groups/${groupId}/expenses`, userId })
}

export function createExpense(
  userId: number,
  groupId: number,
  expense: ExpenseInput,
): Promise<Expense> {
  return apiRequest({ method: 'POST', path: `/groups/${groupId}/expenses`, userId, body: expense })
}

export function recordSettlement(
  userId: number,
  groupId: number,
  settlement: SettlementInput,
): Promise<Settlement> {
  return apiRequest({
    method: 'POST',
    path: `/groups/${groupId}/settlements`,
    userId,
    body: settlement,
  })
}

export function getBalances(userId: number, groupId: number): Promise<Balance[]> {
  return apiRequest({ method: 'GET', path: `/groups/${groupId}/balances`, userId })
}

export function getSettlementPlan(userId: number, groupId: number): Promise<Transfer[]> {
  return apiRequest({ method: 'GET', path: `/groups/${groupId}/settlement-plan`, userId })
}
