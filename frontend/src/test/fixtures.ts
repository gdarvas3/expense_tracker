import type { Expense, Group, Member, User } from '../types/api'

export const ALICE: User = { id: 1, name: 'Alice' }
export const BOB: User = { id: 2, name: 'Bob' }
export const CAROL: User = { id: 3, name: 'Carol' }

export const MEMBERS: Member[] = [
  { user_id: 1, role: 'admin' },
  { user_id: 2, role: 'member' },
]

export const USER_NAMES = new Map([
  [ALICE.id, ALICE.name],
  [BOB.id, BOB.name],
  [CAROL.id, CAROL.name],
])

export const GROUP: Group = {
  id: 10,
  name: 'Flat 4B',
  created_at: '2026-11-03T10:00:00',
  members: MEMBERS,
}

export const GROCERIES: Expense = {
  id: 100,
  description: 'Groceries',
  amount: '80.00',
  payer_id: 1,
  split_type: 'equal',
  created_at: '2026-11-03T10:05:00',
  shares: [
    { user_id: 1, amount: '40.00', percentage: null },
    { user_id: 2, amount: '40.00', percentage: null },
  ],
}
