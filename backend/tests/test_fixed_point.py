"""Tests for decimal ↔ hundredths conversion used for money (cents) and percentages (bp)."""

from decimal import Decimal

import pytest

from app.schemas.fixed_point import format_hundredths, parse_hundredths


@pytest.mark.parametrize(
    ("raw_value", "expected_hundredths"),
    [
        ("100.00", 10000),
        ("100", 10000),
        ("0.01", 1),
        ("33.3", 3330),
        ("-15.00", -1500),
        (100, 10000),
        (25.5, 2550),
        (Decimal("12.34"), 1234),
    ],
)
def test_parse_hundredths_accepts_up_to_two_decimals(
    raw_value: object, expected_hundredths: int
) -> None:
    assert parse_hundredths(raw_value) == expected_hundredths


@pytest.mark.parametrize(
    "raw_value",
    ["1.001", "abc", "", "NaN", "Infinity", True, None, [1]],
)
def test_parse_hundredths_rejects_invalid_values(raw_value: object) -> None:
    with pytest.raises(ValueError):
        parse_hundredths(raw_value)


@pytest.mark.parametrize(
    ("hundredths", "expected_text"),
    [
        (10000, "100.00"),
        (2550, "25.50"),
        (5, "0.05"),
        (0, "0.00"),
        (-1500, "-15.00"),
        (-1, "-0.01"),
    ],
)
def test_format_hundredths_uses_two_decimals(hundredths: int, expected_text: str) -> None:
    assert format_hundredths(hundredths) == expected_text
