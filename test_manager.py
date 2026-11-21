"""Tests for ResultManager (the six functional requirements)."""

from decimal import Decimal

import pytest

from result_manager import (
    CourseNotFoundError,
    DuplicateCourseError,
    DuplicateStudentError,
    InvalidInputError,
    InvalidMarkError,
    ResultManager,
    StudentNotFoundError,
)


@pytest.fixture
def mgr():
    return ResultManager()


@pytest.fixture
def loaded(mgr):
    mgr.add_student("S1", "Alice")
    mgr.add_course("CSE101", "Programming", 3)
    mgr.add_course("CSE102", "Discrete Math", 4)
    mgr.add_course("CSE103", "Physics Lab", 1.5)
    return mgr


# 1. Add a student ---------------------------------------------------------
class TestAddStudent:
    def test_add_student(self, mgr):
        s = mgr.add_student("241077037", "Pritom Kumar Saha")
        assert (s.student_id, s.name) == ("241077037", "Pritom Kumar Saha")
        assert mgr.list_students() == [s]

    def test_duplicate_id_rejected(self, mgr):
        mgr.add_student("1", "A")
        with pytest.raises(DuplicateStudentError):
            mgr.add_student("1", "B")
        assert len(mgr.list_students()) == 1

    def test_duplicate_id_ignores_surrounding_spaces(self, mgr):
        mgr.add_student("1", "A")
        with pytest.raises(DuplicateStudentError):
            mgr.add_student("  1 ", "B")

    @pytest.mark.parametrize("sid, name", [("", "A"), ("  ", "A"), ("1", ""), ("1", "  "), (None, "A"), ("1", None)])
    def test_empty_values_rejected(self, mgr, sid, name):
        with pytest.raises(InvalidInputError):
            mgr.add_student(sid, name)


# 2. Add a course ----------------------------------------------------------
class TestAddCourse:
    def test_add_course(self, mgr):
        c = mgr.add_course("cse402", "Software Lab", "1.5")
        assert (c.code, c.title, c.credits) == ("CSE402", "Software Lab", Decimal("1.5"))

    def test_duplicate_code_rejected(self, mgr):
        mgr.add_course("CSE1", "A", 3)
        with pytest.raises(DuplicateCourseError):
            mgr.add_course("cse1", "B", 3)

    @pytest.mark.parametrize("credits", [0, -1, "abc", "", None, True, "nan", "inf", -0.5])
    def test_bad_credits_rejected(self, mgr, credits):
        with pytest.raises(InvalidInputError):
            mgr.add_course("C1", "T", credits)

    @pytest.mark.parametrize("code, title", [("", "T"), ("C", ""), (" ", "T")])
    def test_empty_code_or_title_rejected(self, mgr, code, title):
        with pytest.raises(InvalidInputError):
            mgr.add_course(code, title, 3)


# 3. Enter marks -----------------------------------------------------------
class TestEnterMarks:
    def test_enter_marks(self, loaded):
        r = loaded.enter_marks("S1", "CSE101", 85)
        assert (r.mark, r.grade, r.grade_point) == (Decimal("85"), "A+", Decimal("4.00"))

    def test_course_code_is_case_insensitive(self, loaded):
        assert loaded.enter_marks("S1", "cse101", 60).grade == "B"

    @pytest.mark.parametrize("mark", [-1, 100.5, 101, "x", None])
    def test_invalid_marks_rejected_and_not_stored(self, loaded, mark):
        with pytest.raises(InvalidMarkError):
            loaded.enter_marks("S1", "CSE101", mark)
        assert loaded.get_result_sheet("S1").rows == []

    def test_unknown_student_or_course(self, loaded):
        with pytest.raises(StudentNotFoundError):
            loaded.enter_marks("NOPE", "CSE101", 50)
        with pytest.raises(CourseNotFoundError):
            loaded.enter_marks("S1", "NOPE", 50)

    def test_re_entering_replaces_mark(self, loaded):
        loaded.enter_marks("S1", "CSE101", 30)
        loaded.enter_marks("S1", "CSE101", 90)
        rows = loaded.get_result_sheet("S1").rows
        assert len(rows) == 1
        assert rows[0].result.mark == Decimal("90")

    def test_boundary_marks_accepted(self, loaded):
        assert loaded.enter_marks("S1", "CSE101", 0).grade == "F"
        assert loaded.enter_marks("S1", "CSE101", 100).grade == "A+"


# 4. Grade and grade point -------------------------------------------------
def test_calculate_grade(mgr):
    assert mgr.calculate_grade(72) == ("A-", Decimal("3.50"))
    assert mgr.calculate_grade("39") == ("F", Decimal("0.00"))
    with pytest.raises(InvalidMarkError):
        mgr.calculate_grade(101)


# 5. CGPA ------------------------------------------------------------------
class TestCgpa:
    def test_no_marks_gives_zero(self, loaded):
        assert loaded.calculate_cgpa("S1") == Decimal("0.00")

    def test_single_course(self, loaded):
        loaded.enter_marks("S1", "CSE101", 77)
        assert loaded.calculate_cgpa("S1") == Decimal("3.75")

    def test_weighted_by_credits(self, loaded):
        loaded.enter_marks("S1", "CSE101", 85)   # 4.00 x 3
        loaded.enter_marks("S1", "CSE102", 62)   # 3.00 x 4
        # (12 + 12) / 7 = 3.428571...
        assert loaded.calculate_cgpa("S1") == Decimal("3.43")

    def test_weighting_differs_from_plain_average(self, loaded):
        loaded.enter_marks("S1", "CSE101", 90)   # 4.00 x 3
        loaded.enter_marks("S1", "CSE102", 10)   # 0.00 x 4
        assert loaded.calculate_cgpa("S1") == Decimal("1.71")  # 12/7, not 2.00

    def test_fractional_credits(self, loaded):
        loaded.enter_marks("S1", "CSE101", 85)   # 4.00 x 3   = 12
        loaded.enter_marks("S1", "CSE103", 50)   # 2.50 x 1.5 = 3.75
        # 15.75 / 4.5 = 3.5
        assert loaded.calculate_cgpa("S1") == Decimal("3.50")

    def test_rounds_half_up(self, mgr):
        mgr.add_student("S", "N")
        mgr.add_course("A", "A", 1)
        mgr.add_course("B", "B", 1)
        mgr.add_course("C", "C", 1)
        mgr.add_course("D", "D", 1)
        # points 4.00 + 3.75 + 3.75 + 3.75 = 15.25 -> /4 = 3.8125 -> 3.81
        for code, mark in (("A", 90), ("B", 77), ("C", 77), ("D", 77)):
            mgr.enter_marks("S", code, mark)
        assert mgr.calculate_cgpa("S") == Decimal("3.81")
        # a second student: 7 x A+ and one A -> exercises rounding of 3.96875
        mgr.add_course("E", "E", 1)
        mgr.add_course("F", "F", 1)
        mgr.add_course("G", "G", 1)
        mgr.add_course("H", "H", 1)
        mgr.add_student("T", "N")
        for code, mark in (("A", 90), ("B", 90), ("C", 90), ("D", 90),
                           ("E", 90), ("F", 90), ("G", 90), ("H", 77)):
            mgr.enter_marks("T", code, mark)
        # (7*4.00 + 3.75) / 8 = 3.96875 -> 3.97
        assert mgr.calculate_cgpa("T") == Decimal("3.97")

    def test_all_failed(self, loaded):
        loaded.enter_marks("S1", "CSE101", 10)
        assert loaded.calculate_cgpa("S1") == Decimal("0.00")

    def test_unknown_student(self, mgr):
        with pytest.raises(StudentNotFoundError):
            mgr.calculate_cgpa("nope")

    def test_cgpa_only_counts_courses_with_marks(self, loaded):
        loaded.enter_marks("S1", "CSE101", 85)  # other courses have no marks
        assert loaded.calculate_cgpa("S1") == Decimal("4.00")

    def test_students_are_independent(self, loaded):
        loaded.add_student("S2", "Bob")
        loaded.enter_marks("S1", "CSE101", 90)
        loaded.enter_marks("S2", "CSE101", 45)
        assert loaded.calculate_cgpa("S1") == Decimal("4.00")
        assert loaded.calculate_cgpa("S2") == Decimal("2.25")


# 6. Result sheet ----------------------------------------------------------
class TestResultSheet:
    def test_sheet_contents(self, loaded):
        loaded.enter_marks("S1", "CSE101", 85)
        loaded.enter_marks("S1", "CSE102", 62)
        sheet = loaded.get_result_sheet("S1")
        assert [r.course.code for r in sheet.rows] == ["CSE101", "CSE102"]
        assert [r.result.grade for r in sheet.rows] == ["A+", "B"]
        assert [r.result.grade_point for r in sheet.rows] == [Decimal("4.00"), Decimal("3.00")]
        assert sheet.total_credits == Decimal("7")
        assert sheet.cgpa == Decimal("3.43")

    def test_rendered_text(self, loaded):
        loaded.enter_marks("S1", "CSE101", 85)
        text = loaded.show_result_sheet("S1")
        for expected in ("RESULT SHEET", "S1", "Alice", "CSE101", "Programming",
                         "85", "A+", "4.00", "CGPA", "4.00"):
            assert expected in text

    def test_empty_sheet(self, loaded):
        text = loaded.show_result_sheet("S1")
        assert "no marks" in text
        assert "0.00" in text

    def test_unknown_student(self, mgr):
        with pytest.raises(StudentNotFoundError):
            mgr.show_result_sheet("nope")

    def test_long_title_is_truncated(self, mgr):
        mgr.add_student("S", "N")
        mgr.add_course("C1", "A very very long course title indeed", 3)
        mgr.enter_marks("S", "C1", 70)
        assert "..." in mgr.show_result_sheet("S")


def test_sheet_shows_fractional_credits_and_marks(mgr):
    mgr.add_student("S", "N")
    mgr.add_course("C1", "Lab", "1.5")
    mgr.enter_marks("S", "C1", "79.5")
    text = mgr.show_result_sheet("S")
    assert "1.5" in text and "79.5" in text and "3.75" in text
