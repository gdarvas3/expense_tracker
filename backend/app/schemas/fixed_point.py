"""Two-decimal fixed-point types: money in cents and percentages in basis points.

Both are "hundredths" of the decimal value the API exchanges (100.00 → 10000 cents,
33.33% → 3333 bp), so one parser and one formatter serve both. Python code works with the
integers; the JSON boundary uses decimal strings.
"""

from decimal import Decimal, InvalidOperation
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer

HUNDREDTHS_PER_UNIT = 100
TWO_DECIMAL_PLACES = Decimal("0.01")
ACCEPTED_INPUT_TYPES = (str, int, float, Decimal)


def parse_hundredths(value: object) -> int:
    """Convert a decimal value with at most two decimal places to an integer of hundredths.

    Raises:
        ValueError: If the value is not a finite number or has more than two decimals.
    """
    decimal_value = to_finite_decimal(value)
    if decimal_value != decimal_value.quantize(TWO_DECIMAL_PLACES):
        raise ValueError("must have at most 2 decimal places")
    return int(decimal_value * HUNDREDTHS_PER_UNIT)


def to_finite_decimal(value: object) -> Decimal:
    # bool is a subclass of int, but True is not a meaningful amount.
    if isinstance(value, bool) or not isinstance(value, ACCEPTED_INPUT_TYPES):
        raise ValueError("must be a decimal number")
    try:
        # str() first, so a float like 25.5 becomes Decimal("25.5"), not its binary expansion.
        decimal_value = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("must be a decimal number") from error
    if not decimal_value.is_finite():
        raise ValueError("must be a finite number")
    return decimal_value


def format_hundredths(hundredths: int) -> str:
    """Format an integer of hundredths as a decimal string with two places, e.g. "-15.00"."""
    return str((Decimal(hundredths) / HUNDREDTHS_PER_UNIT).quantize(TWO_DECIMAL_PLACES))


HundredthsInput = Annotated[int, BeforeValidator(parse_hundredths)]
HundredthsOutput = Annotated[int, PlainSerializer(format_hundredths, return_type=str)]
