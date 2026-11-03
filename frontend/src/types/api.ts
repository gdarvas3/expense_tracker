/**
 * Types mirroring the backend schemas (backend/app/schemas). Amounts and percentages are
 * decimal strings such as "100.00"; the backend is the only place that does money math.
 */

export type SplitType = 'equal' | 'percentage' | 'exact'
export type MemberRole = 'admin' | 'member'

export interface User {
  id: number
  name: string
}

export interface Member {
  user_id: number
  role: MemberRole
}

export interface Group {
  id: number
  name: string
  created_at: string
  members: Member[]
}

export interface Share {
  user_id: number
  amount: string
  percentage: string | null
}

export interface Expense {
  id: number
  description: string
  amount: string
  payer_id: number
  split_type: SplitType
  created_at: string
  shares: Share[]
}

export interface ParticipantInput {
  user_id: number
  amount?: string
  percentage?: string
}

export interface ExpenseInput {
  description: string
  amount: string
  payer_id: number
  split_type: SplitType
  participants: ParticipantInput[]
}

export interface Settlement {
  id: number
  payer_id: number
  payee_id: number
  amount: string
  created_at: string
}

export interface SettlementInput {
  payer_id: number
  payee_id: number
  amount: string
}

export interface Balance {
  user_id: number
  net: string
}

export interface Transfer {
  from_user_id: number
  to_user_id: number
  amount: string
}
