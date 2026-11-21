"""Mark validation and the marks -> (letter grade, grade point) scale."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Tuple, Union

from .exceptions import InvalidMarkError

MarkLike = Union[int, float, Decimal, str]

MIN_MARK = Decimal("0")
MAX_MARK = Decimal("100")

# (lowest mark for the band, letter grade, grade point) - highest band first.
#   80-100 A+ 4.00 | 75-79 A 3.75 | 70-74 A- 3.50 | 65-69 B+ 3.25
#   60-64  B  3.00 | 55-59 B- 2.75 | 50-54 C+ 2.50 | 45-49 C  2.25
#   40-44  D  2.00 | 0-39  F  0.00
GRADE_SCALE = (
    (Decimal("80"), "A+", Decimal("4.00")),
    (Decimal("75"), "A", Decimal("3.75")),
    (Decimal("70"), "A-", Decimal("3.50")),
    (Decimal("65"), "B+", Decimal("3.25")),
    (Decimal("60"), "B", Decimal("3.00")),
    (Decimal("55"), "B-", Decimal("2.75")),
    (Decimal("50"), "C+", Decimal("2.50")),
    (Decimal("45"), "C", Decimal("2.25")),
    (Decimal("40"), "D", Decimal("2.00")),
    (Decimal("0"), "F", Decimal("0.00")),
)


def validate_mark(mark: MarkLike) -> Decimal:
    """Return ``mark`` as a Decimal, or raise InvalidMarkError.

    A valid mark is a finite number with 0 <= mark <= 100.
    Booleans and non-numeric text are rejected.
    """
    if isinstance(mark, bool) or mark is None:
        raise InvalidMarkError(f"Mark must be a number, got {mark!r}.")
    try:
        value = Decimal(str(mark).strip())
    except (InvalidOperation, ValueError):
        raise InvalidMarkError(f"Mark must be a number, got {mark!r}.") from None
    if not value.is_finite():
        raise InvalidMarkError(f"Mark must be a finite number, got {mark!r}.")
    if value < MIN_MARK or value > MAX_MARK:
        raise InvalidMarkError(
            f"Mark must be between 0 and 100 (inclusive), got {value}."
        )
    return value


def get_grade(mark: MarkLike) -> Tuple[str, Decimal]:
    """Return ``(letter_grade, grade_point)`` for a mark out of 100."""
    value = validate_mark(mark)
    for lower_bound, letter, point in GRADE_SCALE:
        if value >= lower_bound:
            return letter, point
    # Unreachable: the last band starts at 0 and value >= 0 is guaranteed.
    raise InvalidMarkError(f"Could not grade mark {value}.")  # pragma: no cover
