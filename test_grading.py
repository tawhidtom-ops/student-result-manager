"""Tests for mark validation and the grade scale."""

from decimal import Decimal

import pytest

from result_manager import InvalidMarkError, get_grade, validate_mark

# (mark, letter, grade point) - every boundary of the scale in the brief.
SCALE_CASES = [
    (100, "A+", "4.00"), (90, "A+", "4.00"), (80, "A+", "4.00"),
    (79, "A", "3.75"), (75, "A", "3.75"),
    (74, "A-", "3.50"), (70, "A-", "3.50"),
    (69, "B+", "3.25"), (65, "B+", "3.25"),
    (64, "B", "3.00"), (60, "B", "3.00"),
    (59, "B-", "2.75"), (55, "B-", "2.75"),
    (54, "C+", "2.50"), (50, "C+", "2.50"),
    (49, "C", "2.25"), (45, "C", "2.25"),
    (44, "D", "2.00"), (40, "D", "2.00"),
    (39, "F", "0.00"), (20, "F", "0.00"), (0, "F", "0.00"),
]


@pytest.mark.parametrize("mark, letter, point", SCALE_CASES)
def test_grade_scale(mark, letter, point):
    assert get_grade(mark) == (letter, Decimal(point))


@pytest.mark.parametrize(
    "mark, letter",
    [(79.5, "A"), (79.99, "A"), (39.9, "F"), (44.5, "D"), (80.0, "A+")],
)
def test_fractional_marks_fall_in_lower_band(mark, letter):
    assert get_grade(mark)[0] == letter


@pytest.mark.parametrize("mark", ["85", " 85 ", "85.0", Decimal("85")])
def test_numeric_strings_and_decimals_are_accepted(mark):
    assert get_grade(mark) == ("A+", Decimal("4.00"))


@pytest.mark.parametrize(
    "mark",
    [-1, -0.01, 100.01, 101, 1000, "abc", "", "  ", None, True, False,
     "nan", "inf", "-inf", float("nan"), float("inf"), [], "12abc"],
)
def test_invalid_marks_are_rejected(mark):
    with pytest.raises(InvalidMarkError):
        validate_mark(mark)
    with pytest.raises(InvalidMarkError):
        get_grade(mark)


def test_boundaries_0_and_100_are_valid():
    assert validate_mark(0) == Decimal("0")
    assert validate_mark(100) == Decimal("100")
