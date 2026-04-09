"""
Input validators for the DocuFlow Version Manager.
"""


class ValidationError(Exception):
    """Raised when user input fails validation."""


def validate_non_empty(value: str, field_name: str) -> str:
    """Return the stripped value if it is non-empty, else raise ValidationError."""
    stripped = value.strip()
    if not stripped:
        raise ValidationError(f"{field_name} must not be empty.")
    return stripped


def validate_positive_integer(value: str, field_name: str) -> int:
    """Parse and return a non-negative integer, or raise ValidationError."""
    stripped = value.strip()
    if not stripped.isdigit():
        raise ValidationError(f"{field_name} must be a non-negative integer.")
    return int(stripped)


def validate_version_fields(
    version_id: str,
    title: str,
    author: str,
    summary: str,
) -> tuple[str, str, str, str]:
    """Validate all fields required to create a DocumentVersion.

    Returns: (version_id, title, author, summary) — all stripped.
    Raises: ValidationError on the first invalid field.
    """
    vid = validate_non_empty(version_id, "Version ID")
    ttl = validate_non_empty(title, "Title")
    aut = validate_non_empty(author, "Author")
    smr = validate_non_empty(summary, "Summary")
    return vid, ttl, aut, smr
