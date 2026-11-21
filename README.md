# Student Result Manager

**Course:** Software Lab (CSE402)
**Student Name:** Pritom Kumar Saha
**Student ID:** 241 077 037

A Python application that lets a teacher record students' marks and produce
their results (letter grade, grade point, CGPA and a result sheet).
Standard library only - no extra packages needed to run it.

## Features (functional requirements)

| # | Requirement | Where |
|---|---|---|
| 1 | Add a student with an ID and a name (IDs must be unique) | `ResultManager.add_student` |
| 2 | Add a course with a code, a title and a credit value | `ResultManager.add_course` |
| 3 | Enter marks out of 100 (below 0 or above 100 is rejected) | `ResultManager.enter_marks` |
| 4 | Calculate letter grade and grade point for a mark | `grading.get_grade`, `ResultManager.calculate_grade` |
| 5 | Calculate a student's CGPA, weighted by course credits | `ResultManager.calculate_cgpa` |
| 6 | Show a student's result sheet (course, mark, grade, grade point, CGPA) | `ResultManager.show_result_sheet` |

### Grade scale

| Marks | Grade | Point |
|---|---|---|
| 80-100 | A+ | 4.00 |
| 75-79 | A | 3.75 |
| 70-74 | A- | 3.50 |
| 65-69 | B+ | 3.25 |
| 60-64 | B | 3.00 |
| 55-59 | B- | 2.75 |
| 50-54 | C+ | 2.50 |
| 45-49 | C | 2.25 |
| 40-44 | D | 2.00 |
| 0-39 | F | 0.00 |

Fractional marks (e.g. 79.5) are accepted and fall in the band below the next
whole-number threshold (79.5 -> A).

### CGPA

```
CGPA = sum(grade point x course credits) / sum(course credits)
```

Only courses in which the student has a mark are counted. The result is
rounded half-up to 2 decimals (`Decimal` is used, so there are no floating
point errors). A student with no marks has CGPA 0.00.

### Design decisions

* Course codes are case-insensitive (`cse402` == `CSE402`) and must be unique.
* Entering marks again for the same student and course **replaces** the old mark.
* Invalid input (empty text, non-numeric mark, credit <= 0, unknown student or
  course) raises a clear `ResultManagerError` subclass; the menu prints it
  instead of crashing.
* Data is kept in memory for the session (persistence was not required).

## Project structure

```
student-result-manager/
├── main.py                  # entry point:  python main.py
├── result_manager/
│   ├── __init__.py
│   ├── cli.py               # menu interface
│   ├── exceptions.py        # custom exceptions
│   ├── grading.py           # mark validation + grade scale
│   ├── manager.py           # ResultManager (business logic)
│   └── models.py            # Student, Course, Result, ResultSheet
├── tests/                   # pytest test-suite (100+ tests)
├── docs/                    # UML diagrams (PNG, .dot sources, Mermaid)
├── .github/workflows/tests.yml   # runs the tests on every push
├── requirements.txt
└── README.md
```

## Run

Python 3.9 or newer.

```bash
python main.py
```

Example session (menu option 6):

```
===================================================================
RESULT SHEET
Student ID : 241077037
Name       : Pritom Kumar Saha
===================================================================
Course    Title                        Credit    Mark  Grade  Point
-------------------------------------------------------------------
CSE402    Software Lab                      3      82     A+   4.00
CSE401    Algorithms                      1.5      66     B+   3.25
-------------------------------------------------------------------
Total credits: 4.5
CGPA         : 3.75
===================================================================
```

Use it from code:

```python
from result_manager import ResultManager

rm = ResultManager()
rm.add_student("241077037", "Pritom Kumar Saha")
rm.add_course("CSE402", "Software Lab", 3)
rm.enter_marks("241077037", "CSE402", 82)
print(rm.show_result_sheet("241077037"))
```

## Testing

```bash
pip install -r requirements.txt
python -m pytest -v
python -m pytest --cov=result_manager --cov-report=term-missing
```

The tests cover every grade boundary (0, 39, 40, 44, 45 ... 79, 80, 100),
invalid marks, duplicate IDs/codes, weighted CGPA (incl. fractional credits
and half-up rounding), the result sheet, and a scripted end-to-end menu session.

## UML

See [docs/UML.md](docs/UML.md): use case diagram, class diagram, exception
hierarchy and sequence diagrams.

## Git / GitHub

```bash
git init
git add .
git commit -m "Student Result Manager - CSE402"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
