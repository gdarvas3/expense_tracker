"""Debt simplification (AC-4) — implementation written with Claude Code."""

from app.services.settlement.transfer import Transfer


def simplify_debts(balances: dict[int, int]) -> list[Transfer]:
    """Greedily match the largest debtor with the largest creditor until all balances are 0."""
    raise NotImplementedError
