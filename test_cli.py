"""End-to-end test of the menu interface using scripted input."""

from result_manager.cli import run


def _session(lines):
    answers = iter(lines)
    out = []
    run(input_fn=lambda prompt: next(answers), output_fn=out.append)
    return "\n".join(out)


def test_full_session():
    text = _session([
        "1", "241077037", "Pritom Kumar Saha",
        "2", "CSE402", "Software Lab", "3",
        "3", "241077037", "CSE402", "82",
        "4", "66",
        "5", "241077037",
        "6", "241077037",
        "7",
        "0",
    ])
    assert "Added student 241077037" in text
    assert "Added course CSE402" in text
    assert "grade A+" in text
    assert "Grade: B+, grade point: 3.25" in text
    assert "CGPA: 4.00" in text
    assert "RESULT SHEET" in text
    assert "Goodbye!" in text


def test_errors_are_reported_not_raised():
    text = _session([
        "1", "1", "A",
        "1", "1", "B",            # duplicate ID
        "2", "C1", "T", "3",
        "3", "1", "C1", "101",    # mark out of range
        "3", "9", "C1", "50",     # unknown student
        "9",                      # invalid menu option
        "0",
    ])
    assert "already exists" in text
    assert "between 0 and 100" in text
    assert "No student with ID '9'" in text
    assert "Invalid option" in text


def test_exit_on_eof():
    def boom(prompt):
        raise EOFError
    run(input_fn=boom, output_fn=lambda s: None)
