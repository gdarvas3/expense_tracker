import type { ReactElement } from 'react'
import type { Transfer } from '../types/api'

interface SettlementPlanProps {
  transfers: Transfer[]
  userNames: Map<number, string>
}

/** The simplified list of payments computed by the backend (AC-4). */
export function SettlementPlan({ transfers, userNames }: SettlementPlanProps): ReactElement {
  function nameOf(userId: number): string {
    return userNames.get(userId) ?? `User ${userId}`
  }

  function renderTransfer(transfer: Transfer): ReactElement {
    return (
      <li key={`${transfer.from_user_id}-${transfer.to_user_id}`} className="slip">
        <span className="slip-label" aria-hidden="true">
          IOU
        </span>
        <span className="slip-text">
          {nameOf(transfer.from_user_id)} pays {nameOf(transfer.to_user_id)} {transfer.amount}
        </span>
      </li>
    )
  }

  if (transfers.length === 0) {
    return <p>Everyone is settled up.</p>
  }
  return <ul className="slips">{transfers.map(renderTransfer)}</ul>
}
