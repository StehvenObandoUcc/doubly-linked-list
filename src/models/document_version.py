"""
DocumentVersion model.

Represents a single version of a technical document
within the DocuFlow Version Manager system.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DocumentVersion:
    """Domain entity representing one version of a technical document."""

    version_id: str
    title: str
    author: str
    summary: str
    status: str = "Draft"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __str__(self) -> str:
        return f"[{self.version_id}] {self.title} by {self.author} ({self.status})"
