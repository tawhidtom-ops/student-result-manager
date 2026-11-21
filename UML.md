# UML Diagrams - Student Result Manager

PNG versions (made from the `.dot` files in this folder):

| Diagram | File |
|---|---|
| Use case diagram | [use_case_diagram.png](use_case_diagram.png) |
| Class diagram | [class_diagram.png](class_diagram.png) |
| Exception hierarchy | [exceptions_diagram.png](exceptions_diagram.png) |

![Use case diagram](use_case_diagram.png)
![Class diagram](class_diagram.png)
![Exception hierarchy](exceptions_diagram.png)

## Sequence diagram - "Show a student's result sheet" (GitHub renders this)

```mermaid
sequenceDiagram
    actor Teacher
    participant CLI as cli.run()
    participant RM as ResultManager
    participant G as grading
    Teacher->>CLI: choose option 6, enter student ID
    CLI->>RM: show_result_sheet(student_id)
    RM->>RM: get_result_sheet(student_id)
    RM->>RM: calculate_cgpa(student_id)
    Note over RM: CGPA = sum(grade point x credits) / sum(credits)
    RM-->>CLI: ResultSheet.render() text
    CLI-->>Teacher: print result sheet
```

## Sequence diagram - "Enter marks"

```mermaid
sequenceDiagram
    actor Teacher
    participant CLI as cli.run()
    participant RM as ResultManager
    participant G as grading
    Teacher->>CLI: option 3 (student ID, course code, mark)
    CLI->>RM: enter_marks(student_id, course_code, mark)
    RM->>RM: find student and course
    RM->>G: validate_mark(mark)
    alt mark < 0 or mark > 100 or not a number
        G-->>RM: raise InvalidMarkError
        RM-->>CLI: error
        CLI-->>Teacher: "Error: Mark must be between 0 and 100"
    else valid mark
        G-->>RM: Decimal mark
        RM->>G: get_grade(mark)
        G-->>RM: (letter, grade point)
        RM->>RM: store Result
        RM-->>CLI: Result
        CLI-->>Teacher: "Saved: mark -> grade, grade point"
    end
```
