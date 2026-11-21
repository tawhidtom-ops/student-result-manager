"""Custom exceptions used by the Student Result Manager."""


class ResultManagerError(Exception):
    """Base class for all errors raised by this application."""


class InvalidInputError(ResultManagerError):
    """Raised when a name, ID, code, title or credit value is invalid."""


class InvalidMarkError(ResultManagerError):
    """Raised when a mark is not a number or is outside the range 0-100."""


class DuplicateStudentError(ResultManagerError):
    """Raised when a student ID already exists (IDs must be unique)."""


class DuplicateCourseError(ResultManagerError):
    """Raised when a course code already exists."""


class StudentNotFoundError(ResultManagerError):
    """Raised when a student ID does not exist."""


class CourseNotFoundError(ResultManagerError):
    """Raised when a course code does not exist."""
