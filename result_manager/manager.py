"""Core business logic: ResultManager."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Dict, List, Tuple, Union

from .exceptions import (
    CourseNotFoundError,
    DuplicateCourseError,
    DuplicateStudentError,
    InvalidInputError,
    StudentNotFoundError,
)
from .grading import MarkLike, get_grade, validate_mark
from .models import Course, Result, ResultRow, ResultSheet, Student

CreditLike = Union[int, float, Decimal, str]
_TWO_PLACES = Decimal("0.01")


class ResultManager:
    """Keeps students, courses and marks in memory and computes results."""

    def __init__(self) -> None:
        self._students: Dict[str, Student] = {}
        self._courses: Dict[str, Course] = {}
        # student_id -> {course_code -> Result}
        self._results: Dict[str, Dict[str, Result]] = {}

    # ------------------------------------------------------------ helpers
    @staticmethod
    def _clean_text(value: object, what: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise InvalidInputError(f"{what} must not be empty.")
        return " ".join(value.split())

    @staticmethod
    def _normalise_code(code: object) -> str:
        return ResultManager._clean_text(code, "Course code").upper()

    def _get_student(self, student_id: str) -> Student:
        key = self._clean_text(student_id, "Student ID")
        try:
            return self._students[key]
        except KeyError:
            raise StudentNotFoundError(f"No student with ID '{key}'.") from None

    def _get_course(self, code: str) -> Course:
        key = self._normalise_code(code)
        try:
            return self._courses[key]
        except KeyError:
            raise CourseNotFoundError(f"No course with code '{key}'.") from None

    # ------------------------------------------------- 1. add a student
    def add_student(self, student_id: str, name: str) -> Student:
        """Add a student. IDs must be unique."""
        student_id = self._clean_text(student_id, "Student ID")
        name = self._clean_text(name, "Student name")
        if student_id in self._students:
            raise DuplicateStudentError(
                f"Student ID '{student_id}' already exists."
            )
        student = Student(student_id, name)
        self._students[student_id] = student
        self._results[student_id] = {}
        return student

    # -------------------------------------------------- 2. add a course
    def add_course(self, code: str, title: str, credits: CreditLike) -> Course:
        """Add a course with a code, a title and a (positive) credit value."""
        code = self._normalise_code(code)
        title = self._clean_text(title, "Course title")
        if isinstance(credits, bool):
            raise InvalidInputError("Credit must be a positive number.")
        try:
            credit_value = Decimal(str(credits).strip())
        except (InvalidOperation, ValueError):
            raise InvalidInputError(
                f"Credit must be a positive number, got {credits!r}."
            ) from None
        if not credit_value.is_finite() or credit_value <= 0:
            raise InvalidInputError(
                f"Credit must be a positive number, got {credits!r}."
            )
        if code in self._courses:
            raise DuplicateCourseError(f"Course code '{code}' already exists.")
        course = Course(code, title, credit_value)
        self._courses[code] = course
        return course

    # -------------------------------------------------- 3. enter marks
    def enter_marks(
        self, student_id: str, course_code: str, mark: MarkLike
    ) -> Result:
        """Record a mark (0-100) for a student in a course.

        Entering marks again for the same student and course replaces the
        earlier mark. Marks below 0 or above 100 are rejected.
        """
        student = self._get_student(student_id)
        course = self._get_course(course_code)
        value = validate_mark(mark)
        grade, point = get_grade(value)
        result = Result(course.code, value, grade, point)
        self._results[student.student_id][course.code] = result
        return result

    # ----------------------------------- 4. letter grade and grade point
    @staticmethod
    def calculate_grade(mark: MarkLike) -> Tuple[str, Decimal]:
        """Return (letter grade, grade point) for a mark."""
        return get_grade(mark)

    # ----------------------------------------------------- 5. the CGPA
    def calculate_cgpa(self, student_id: str) -> Decimal:
        """Credit-weighted CGPA, rounded half-up to 2 decimals.

        CGPA = sum(grade_point * credits) / sum(credits), over the courses
        in which the student has marks. Returns 0.00 if there are none.
        """
        student = self._get_student(student_id)
        total_points = Decimal("0")
        total_credits = Decimal("0")
        for code, result in self._results[student.student_id].items():
            credits = self._courses[code].credits
            total_points += result.grade_point * credits
            total_credits += credits
        if total_credits == 0:
            return Decimal("0.00")
        return (total_points / total_credits).quantize(
            _TWO_PLACES, rounding=ROUND_HALF_UP
        )

    # -------------------------------------------- 6. the result sheet
    def get_result_sheet(self, student_id: str) -> ResultSheet:
        student = self._get_student(student_id)
        rows: List[ResultRow] = []
        total_credits = Decimal("0")
        for code, result in self._results[student.student_id].items():
            course = self._courses[code]
            rows.append(ResultRow(course, result))
            total_credits += course.credits
        return ResultSheet(
            student=student,
            rows=rows,
            total_credits=total_credits,
            cgpa=self.calculate_cgpa(student.student_id),
        )

    def show_result_sheet(self, student_id: str) -> str:
        """Return the printable result sheet for a student."""
        return self.get_result_sheet(student_id).render()

    # ---------------------------------------------------- extra helpers
    def list_students(self) -> List[Student]:
        return list(self._students.values())

    def list_courses(self) -> List[Course]:
        return list(self._courses.values())
