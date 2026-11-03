from sqlalchemy.orm import Session

from app.models import Group


def calculate_balances(db: Session, group: Group) -> dict[int, int]:
    """Return each member's net balance in cents; positive means the others owe them."""
    raise NotImplementedError
