"""
DocumentTimeline — manually implemented doubly linked list.

Stores the full timeline of a document as a chain
of RevisionChainLink objects linked via prev/next pointers.
No Python native list is used as the source of truth.
"""

from __future__ import annotations

from src.models.document_version import DocumentVersion
from src.data_structures.revision_chain_link import RevisionChainLink


class DocumentTimeline:
    """Doubly linked list that manages the chronological timeline of document revisions."""

    def __init__(self) -> None:
        self.head: RevisionChainLink | None = None
        self.tail: RevisionChainLink | None = None
        self.current: RevisionChainLink | None = None
        self.size: int = 0

    # ------------------------------------------------------------------
    # Capacity helpers
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Return True if the timeline contains no versions."""
        return self.size == 0

    # ------------------------------------------------------------------
    # Insertion operations
    # ------------------------------------------------------------------

    def append_version(self, version: DocumentVersion) -> None:
        """Add a version at the end of the timeline."""
        new_link = RevisionChainLink(data=version)

        if self.is_empty():
            self.head = self.tail = self.current = new_link
        else:
            new_link.prev = self.tail
            self.tail.next = new_link  # type: ignore[union-attr]
            self.tail = new_link

        self.size += 1

    def prepend_version(self, version: DocumentVersion) -> None:
        """Add a version at the beginning of the timeline."""
        new_link = RevisionChainLink(data=version)

        if self.is_empty():
            self.head = self.tail = self.current = new_link
        else:
            new_link.next = self.head
            self.head.prev = new_link  # type: ignore[union-attr]
            self.head = new_link

        self.size += 1

    def insert_version_at(self, index: int, version: DocumentVersion) -> None:
        """Insert a version at the given zero-based index.

        Raises:
            IndexError: If the index is out of the valid range [0, size].
        """
        if index < 0 or index > self.size:
            raise IndexError(f"Index {index} is out of range [0, {self.size}].")

        if index == 0:
            self.prepend_version(version)
            return

        if index == self.size:
            self.append_version(version)
            return

        target = self._walk_to(index)
        new_link = RevisionChainLink(data=version)

        new_link.prev = target.prev
        new_link.next = target
        target.prev.next = new_link  # type: ignore[union-attr]
        target.prev = new_link

        self.size += 1

    # ------------------------------------------------------------------
    # Removal operations
    # ------------------------------------------------------------------

    def remove_version_at(self, index: int) -> DocumentVersion:
        """Remove and return the version at the given zero-based index.

        Raises:
            IndexError: If the timeline is empty or the index is invalid.
        """
        if self.is_empty():
            raise IndexError("Cannot remove from an empty timeline.")
        if index < 0 or index >= self.size:
            raise IndexError(f"Index {index} is out of range [0, {self.size - 1}].")

        target = self._walk_to(index)
        return self._unlink(target)

    def remove_current_version(self) -> DocumentVersion:
        """Remove and return the version that is currently selected.

        After removal, the current pointer moves to the next link if
        available; otherwise it falls back to the previous link.

        Raises:
            IndexError: If there is no current version.
        """
        if self.current is None:
            raise IndexError("No current version to remove.")

        link = self.current

        if link.next is not None:
            self.current = link.next
        elif link.prev is not None:
            self.current = link.prev
        else:
            self.current = None

        return self._unlink(link)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def move_next(self) -> bool:
        """Move the current pointer to the next version.

        Returns True if the move succeeded, False if already at the tail.
        """
        if self.current is not None and self.current.next is not None:
            self.current = self.current.next
            return True
        return False

    def move_previous(self) -> bool:
        """Move the current pointer to the previous version.

        Returns True if the move succeeded, False if already at the head.
        """
        if self.current is not None and self.current.prev is not None:
            self.current = self.current.prev
            return True
        return False

    # ------------------------------------------------------------------
    # Lookup / query
    # ------------------------------------------------------------------

    def get_current_version(self) -> DocumentVersion | None:
        """Return the data of the currently selected link, or None."""
        if self.current is not None:
            return self.current.data
        return None

    def get_version_at(self, index: int) -> DocumentVersion:
        """Return the version at the given zero-based index.

        Raises:
            IndexError: If the index is out of range.
        """
        if index < 0 or index >= self.size:
            raise IndexError(f"Index {index} is out of range [0, {self.size - 1}].")
        return self._walk_to(index).data

    def find_version_by_id(self, version_id: str) -> DocumentVersion | None:
        """Return the first version whose ID matches, or None."""
        link = self.head
        while link is not None:
            if link.data.version_id == version_id:
                return link.data
            link = link.next
        return None

    def find_versions_by_author(self, author: str) -> list[DocumentVersion]:
        """Return all versions whose author contains the given substring (case-insensitive)."""
        results: list[DocumentVersion] = []
        author_lower = author.lower()
        link = self.head
        while link is not None:
            if author_lower in link.data.author.lower():
                results.append(link.data)
            link = link.next
        return results

    # ------------------------------------------------------------------
    # Traversal (returns temporary Python lists for UI rendering only)
    # ------------------------------------------------------------------

    def to_list_forward(self) -> list[DocumentVersion]:
        """Traverse from head to tail and return versions in ascending order."""
        versions: list[DocumentVersion] = []
        link = self.head
        while link is not None:
            versions.append(link.data)
            link = link.next
        return versions

    def to_list_backward(self) -> list[DocumentVersion]:
        """Traverse from tail to head and return versions in descending order."""
        versions: list[DocumentVersion] = []
        link = self.tail
        while link is not None:
            versions.append(link.data)
            link = link.prev
        return versions

    # ------------------------------------------------------------------
    # Current-position index helper (used by UI to highlight selection)
    # ------------------------------------------------------------------

    def get_current_index(self) -> int:
        """Return the zero-based index of the current link, or -1 if none."""
        if self.current is None:
            return -1
        idx = 0
        link = self.head
        while link is not None:
            if link is self.current:
                return idx
            idx += 1
            link = link.next
        return -1

    def set_current_by_index(self, index: int) -> None:
        """Set the current pointer to the link at the given index.

        Raises:
            IndexError: If the index is out of range.
        """
        if index < 0 or index >= self.size:
            raise IndexError(f"Index {index} is out of range [0, {self.size - 1}].")
        self.current = self._walk_to(index)

    # ------------------------------------------------------------------
    # Reorder (move a link to a different position)
    # ------------------------------------------------------------------

    def move_version(self, from_index: int, to_index: int) -> None:
        """Move the link at *from_index* to *to_index* via pointer manipulation.

        The current pointer follows the moved link.

        Raises:
            IndexError: If either index is out of range.
        """
        if from_index == to_index:
            return
        if from_index < 0 or from_index >= self.size:
            raise IndexError(f"Source index {from_index} is out of range [0, {self.size - 1}].")
        if to_index < 0 or to_index >= self.size:
            raise IndexError(f"Target index {to_index} is out of range [0, {self.size - 1}].")

        link = self._walk_to(from_index)

        # Step 1: Unlink from current position
        if link.prev is not None:
            link.prev.next = link.next
        else:
            self.head = link.next

        if link.next is not None:
            link.next.prev = link.prev
        else:
            self.tail = link.prev

        # Step 2: Re-link at target position
        effective_target = to_index if to_index < from_index else to_index

        if effective_target == 0:
            link.prev = None
            link.next = self.head
            if self.head is not None:
                self.head.prev = link
            self.head = link
            if self.tail is None:
                self.tail = link
        elif effective_target >= self.size - 1:
            link.next = None
            link.prev = self.tail
            if self.tail is not None:
                self.tail.next = link
            self.tail = link
            if self.head is None:
                self.head = link
        else:
            target_link = self.head
            for _ in range(effective_target):
                target_link = target_link.next  # type: ignore[union-attr]

            link.prev = target_link.prev  # type: ignore[union-attr]
            link.next = target_link
            if target_link.prev is not None:  # type: ignore[union-attr]
                target_link.prev.next = link  # type: ignore[union-attr]
            else:
                self.head = link
            target_link.prev = link  # type: ignore[union-attr]

        self.current = link

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _walk_to(self, index: int) -> RevisionChainLink:
        """Walk from whichever end is closer and return the link at *index*."""
        if index <= self.size // 2:
            link = self.head
            for _ in range(index):
                link = link.next  # type: ignore[union-attr]
        else:
            link = self.tail
            for _ in range(self.size - 1 - index):
                link = link.prev  # type: ignore[union-attr]
        return link  # type: ignore[return-value]

    def _unlink(self, link: RevisionChainLink) -> DocumentVersion:
        """Remove *link* from the chain and return its data."""
        if link.prev is not None:
            link.prev.next = link.next
        else:
            self.head = link.next

        if link.next is not None:
            link.next.prev = link.prev
        else:
            self.tail = link.prev

        self.size -= 1

        if self.size == 0:
            self.head = self.tail = self.current = None

        data = link.data
        link.prev = link.next = None
        return data
