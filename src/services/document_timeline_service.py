"""
DocumentTimelineService — business-logic facade.

All UI interactions go through this service.
The UI never manipulates linked-list pointers directly.
"""

from src.models.document_version import DocumentVersion
from src.data_structures.document_timeline import DocumentTimeline
from src.utils.validators import validate_version_fields, validate_positive_integer, ValidationError


class DocumentTimelineService:
    """Coordinates operations between the user interface and the document timeline data structure."""

    def __init__(self) -> None:
        self._timeline = DocumentTimeline()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def timeline_size(self) -> int:
        """Return the number of versions currently stored."""
        return self._timeline.size

    @property
    def is_empty(self) -> bool:
        """Return True if no versions exist."""
        return self._timeline.is_empty()

    @property
    def current_index(self) -> int:
        """Return the zero-based index of the current version (-1 if empty)."""
        return self._timeline.get_current_index()

    # ------------------------------------------------------------------
    # Create / insert
    # ------------------------------------------------------------------

    def create_version(
        self,
        version_id: str,
        title: str,
        author: str,
        summary: str,
        status: str = "Draft",
    ) -> DocumentVersion:
        """Validate inputs, build a DocumentVersion, and append it to the timeline.

        Returns the newly created version.
        Raises ValidationError on bad input.
        """
        vid, ttl, aut, smr = validate_version_fields(version_id, title, author, summary)
        status = status.strip() or "Draft"

        if self._timeline.find_version_by_id(vid) is not None:
            raise ValidationError(f"A version with ID '{vid}' already exists.")

        version = DocumentVersion(
            version_id=vid,
            title=ttl,
            author=aut,
            summary=smr,
            status=status,
        )
        self._timeline.append_version(version)
        return version

    def insert_version(
        self,
        position: str | int,
        version_id: str,
        title: str,
        author: str,
        summary: str,
        status: str = "Draft",
    ) -> DocumentVersion:
        """Validate inputs and insert a version at the given position.

        *position* can be a string (will be parsed) or int.
        Raises ValidationError on bad input or IndexError on invalid position.
        """
        if isinstance(position, str):
            idx = validate_positive_integer(position, "Position")
        else:
            idx = position

        vid, ttl, aut, smr = validate_version_fields(version_id, title, author, summary)
        status = status.strip() or "Draft"

        if self._timeline.find_version_by_id(vid) is not None:
            raise ValidationError(f"A version with ID '{vid}' already exists.")

        version = DocumentVersion(
            version_id=vid,
            title=ttl,
            author=aut,
            summary=smr,
            status=status,
        )
        self._timeline.insert_version_at(idx, version)
        return version

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_version_at(self, index: int) -> DocumentVersion:
        """Remove the version at *index* and return it.

        Raises IndexError if the index is invalid.
        """
        return self._timeline.remove_version_at(index)

    def delete_current_version(self) -> DocumentVersion:
        """Remove the currently selected version.

        Raises IndexError if there is no current version.
        """
        return self._timeline.remove_current_version()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def go_to_next_version(self) -> bool:
        """Move to the next version. Returns True on success."""
        return self._timeline.move_next()

    def go_to_previous_version(self) -> bool:
        """Move to the previous version. Returns True on success."""
        return self._timeline.move_previous()

    def select_version_at(self, index: int) -> None:
        """Set the current pointer to the version at *index*."""
        self._timeline.set_current_by_index(index)

    def reorder_version(self, from_index: int, to_index: int) -> None:
        """Move a version from one position to another in the timeline.

        Raises IndexError if either index is out of range.
        """
        self._timeline.move_version(from_index, to_index)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_current_version_data(self) -> DocumentVersion | None:
        """Return the data of the current version, or None."""
        return self._timeline.get_current_version()

    def get_all_versions_forward(self) -> list[DocumentVersion]:
        """Return all versions in ascending (head→tail) order."""
        return self._timeline.to_list_forward()

    def get_all_versions_backward(self) -> list[DocumentVersion]:
        """Return all versions in descending (tail→head) order."""
        return self._timeline.to_list_backward()

    def search_versions(self, query: str) -> list[DocumentVersion]:
        """Search by version ID (exact) or author (substring).

        Returns matching versions. An exact ID match is returned first.
        """
        results: list[DocumentVersion] = []
        exact = self._timeline.find_version_by_id(query)
        if exact is not None:
            results.append(exact)

        by_author = self._timeline.find_versions_by_author(query)
        for v in by_author:
            if v not in results:
                results.append(v)

        return results

    # ------------------------------------------------------------------
    # Sample data (for demonstration / initial load)
    # ------------------------------------------------------------------

    def load_sample_data(self) -> None:
        """Populate the timeline with a few example document versions."""
        samples = [
            ("v1.0", "Initial Architecture Proposal", "Alice Chen", "First draft of the system architecture document.", "Approved"),
            ("v1.1", "Architecture Review Notes", "Bob Martinez", "Incorporated feedback from the review board.", "Approved"),
            ("v1.2", "Security Appendix Added", "Carol Nguyen", "Added the security analysis appendix.", "In Review"),
            ("v2.0", "Major Redesign Draft", "Alice Chen", "Complete redesign based on new requirements.", "Draft"),
        ]
        for vid, title, author, summary, status in samples:
            self.create_version(vid, title, author, summary, status)
