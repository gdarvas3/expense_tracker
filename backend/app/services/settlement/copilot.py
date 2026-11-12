"""Copilot debt-simplification implementation."""

import heapq

from .transfer import Transfer


def simplify_debts(balances: dict[int, int]) -> list[Transfer]:
    """Simplify balanced debts into deterministic transfers."""
    if sum(balances.values()) != 0:
        raise ValueError("Balances must sum to zero.")

    remaining_balances = dict(balances)
    debtor_heap = [
        (-abs(balance_cents), user_id)
        for user_id, balance_cents in remaining_balances.items()
        if balance_cents < 0
    ]
    creditor_heap = [
        (-balance_cents, user_id)
        for user_id, balance_cents in remaining_balances.items()
        if balance_cents > 0
    ]
    heapq.heapify(debtor_heap)
    heapq.heapify(creditor_heap)

    transfers: list[Transfer] = []
    while debtor_heap and creditor_heap:
        debtor_priority, debtor_id = heapq.heappop(debtor_heap)
        creditor_priority, creditor_id = heapq.heappop(creditor_heap)
        debtor_balance_cents = -debtor_priority
        creditor_balance_cents = -creditor_priority

        transfer_amount_cents = min(debtor_balance_cents, creditor_balance_cents)
        transfers.append(
            Transfer(
                from_user_id=debtor_id,
                to_user_id=creditor_id,
                amount_cents=transfer_amount_cents,
            )
        )

        remaining_debt_cents = debtor_balance_cents - transfer_amount_cents
        if remaining_debt_cents:
            heapq.heappush(debtor_heap, (-remaining_debt_cents, debtor_id))

        remaining_credit_cents = creditor_balance_cents - transfer_amount_cents
        if remaining_credit_cents:
            heapq.heappush(creditor_heap, (-remaining_credit_cents, creditor_id))

    return transfers
