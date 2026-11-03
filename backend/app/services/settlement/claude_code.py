"""Debt simplification (AC-4) — implementation written with Claude Code."""

from app.services.settlement.transfer import Transfer


def simplify_debts(balances: dict[int, int]) -> list[Transfer]:
    """Greedily match the largest debtor with the largest creditor until all balances are 0.

    Ties are broken by ascending user ID, so the plan is deterministic.

    Raises:
        ValueError: If the balances do not sum to zero.
    """
    if sum(balances.values()) != 0:
        raise ValueError("Balances must sum to zero.")
    open_balances = {user_id: net for user_id, net in balances.items() if net != 0}
    transfers: list[Transfer] = []
    while open_balances:
        transfers.append(settle_largest_pair(open_balances))
    return transfers


def settle_largest_pair(open_balances: dict[int, int]) -> Transfer:
    """Pay as much as possible from the largest debtor to the largest creditor.

    Updates open_balances in place and drops whoever is settled; at least one party is,
    so the caller's loop always terminates.
    """
    debtor_id = largest_debtor(open_balances)
    creditor_id = largest_creditor(open_balances)
    amount_cents = min(-open_balances[debtor_id], open_balances[creditor_id])

    open_balances[debtor_id] += amount_cents
    open_balances[creditor_id] -= amount_cents
    for user_id in (debtor_id, creditor_id):
        if open_balances[user_id] == 0:
            del open_balances[user_id]
    return Transfer(from_user_id=debtor_id, to_user_id=creditor_id, amount_cents=amount_cents)


def largest_creditor(open_balances: dict[int, int]) -> int:
    # Negated IDs make max() prefer the lowest user ID among equal amounts.
    _, negated_user_id = max(
        (net, -user_id) for user_id, net in open_balances.items() if net > 0
    )
    return -negated_user_id


def largest_debtor(open_balances: dict[int, int]) -> int:
    _, negated_user_id = max(
        (-net, -user_id) for user_id, net in open_balances.items() if net < 0
    )
    return -negated_user_id
