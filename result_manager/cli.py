"""Menu-driven command line interface for the Student Result Manager."""

from __future__ import annotations

from typing import Callable, Optional

from .exceptions import ResultManagerError
from .manager import ResultManager

MENU = """
===== Student Result Manager =====
1. Add a student
2. Add a course
3. Enter marks
4. Calculate grade for a mark
5. Calculate a student's CGPA
6. Show a student's result sheet
7. List students and courses
0. Exit
"""


def run(
    manager: Optional[ResultManager] = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> None:
    """Run the interactive menu. input_fn/output_fn are injectable for tests."""
    manager = manager or ResultManager()
    while True:
        output_fn(MENU)
        try:
            choice = input_fn("Choose an option: ").strip()
        except EOFError:
            return
        try:
            if choice == "0":
                output_fn("Goodbye!")
                return
            elif choice == "1":
                sid = input_fn("Student ID: ")
                name = input_fn("Student name: ")
                s = manager.add_student(sid, name)
                output_fn(f"Added student {s.student_id} - {s.name}.")
            elif choice == "2":
                code = input_fn("Course code: ")
                title = input_fn("Course title: ")
                credits = input_fn("Credit value: ")
                c = manager.add_course(code, title, credits)
                output_fn(f"Added course {c.code} - {c.title} ({c.credits} credits).")
            elif choice == "3":
                sid = input_fn("Student ID: ")
                code = input_fn("Course code: ")
                mark = input_fn("Mark (0-100): ")
                r = manager.enter_marks(sid, code, mark)
                output_fn(
                    f"Saved: mark {r.mark} -> grade {r.grade}, "
                    f"grade point {r.grade_point:.2f}."
                )
            elif choice == "4":
                mark = input_fn("Mark (0-100): ")
                grade, point = manager.calculate_grade(mark)
                output_fn(f"Grade: {grade}, grade point: {point:.2f}")
            elif choice == "5":
                sid = input_fn("Student ID: ")
                output_fn(f"CGPA: {manager.calculate_cgpa(sid):.2f}")
            elif choice == "6":
                sid = input_fn("Student ID: ")
                output_fn(manager.show_result_sheet(sid))
            elif choice == "7":
                output_fn("Students:")
                for s in manager.list_students():
                    output_fn(f"  {s.student_id} - {s.name}")
                output_fn("Courses:")
                for c in manager.list_courses():
                    output_fn(f"  {c.code} - {c.title} ({c.credits} credits)")
            else:
                output_fn("Invalid option. Please choose 0-7.")
        except ResultManagerError as error:
            output_fn(f"Error: {error}")
