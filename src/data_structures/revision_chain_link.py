"""
RevisionChainLink — doubly linked list node.

Each link wraps a DocumentVersion and holds references
to the previous and next links in the document timeline chain.
"""

from __future__ import annotations

from src.models.document_version import DocumentVersion


class RevisionChainLink:
    """A single link in the document timeline doubly linked list."""

    __slots__ = ("data", "prev", "next")

    def __init__(
        self,
        data: DocumentVersion,
        prev: RevisionChainLink | None = None,
        next: RevisionChainLink | None = None,
    ) -> None:
        self.data: DocumentVersion = data
        self.prev: RevisionChainLink | None = prev
        self.next: RevisionChainLink | None = next

    def __repr__(self) -> str:
        return f"RevisionChainLink({self.data.version_id})"
