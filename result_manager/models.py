"""Data classes: Student, Course, Result, ResultRow and ResultSheet."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


def format_number(value: Decimal) -> str:
    """Format a Decimal without trailing zeros, e.g. 80 -> '80', 79.5 -> '79.5'."""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


@dataclass(frozen=True)
class Student:
    student_id: str
    name: str


@dataclass(frozen=True)
class Course:
    code: str
    title: str
    credits: Decimal


@dataclass(frozen=True)
class Result:
    """A student's mark in one course together with the derived grade."""

    course_code: str
    mark: Decimal
    grade: str
    grade_point: Decimal


@dataclass(frozen=True)
class ResultRow:
    """One line of a result sheet (course details + result)."""

    course: Course
    result: Result


@dataclass(frozen=True)
class ResultSheet:
    student: Student
    rows: List[ResultRow] = field(default_factory=list)
    total_credits: Decimal = Decimal("0")
    cgpa: Decimal = Decimal("0.00")

    def render(self) -> str:
        """Return the sheet as printable text."""
        header = (
            f"{'Course':<10}{'Title':<28}{'Credit':>7}"
            f"{'Mark':>8}{'Grade':>7}{'Point':>7}"
        )
        line = "=" * len(header)
        out = [
            line,
            "RESULT SHEET",
            f"Student ID : {self.student.student_id}",
            f"Name       : {self.student.name}",
            line,
            header,
            "-" * len(header),
        ]
        if not self.rows:
            out.append("(no marks have been entered yet)")
        for row in self.rows:
            title = row.course.title
            if len(title) > 26:
                title = title[:23] + "..."
            out.append(
                f"{row.course.code:<10}{title:<28}"
                f"{format_number(row.course.credits):>7}"
                f"{format_number(row.result.mark):>8}"
                f"{row.result.grade:>7}"
                f"{row.result.grade_point:>7.2f}"
            )
        out.append("-" * len(header))
        out.append(f"Total credits: {format_number(self.total_credits)}")
        out.append(f"CGPA         : {self.cgpa:.2f}")
        out.append(line)
        return "\n".join(out)
