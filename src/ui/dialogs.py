"""
Modal dialogs for creating and inserting document versions.
"""

import tkinter as tk
from tkinter import ttk

from src.ui.components import COLORS, FONT_FAMILY, StyledButton
from src.utils.validators import ValidationError, validate_version_fields, validate_positive_integer


class _BaseVersionDialog(tk.Toplevel):
    """Base dialog for entering version details."""

    def __init__(self, parent: tk.Widget, title: str) -> None:
        super().__init__(parent)
        self.title(title)
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        self.result: dict[str, str] | None = None

        # Center on parent
        self.update_idletasks()
        self.geometry("+%d+%d" % (
            parent.winfo_rootx() + 120,
            parent.winfo_rooty() + 80,
        ))

        self._entries: dict[str, tk.Entry] = {}
        self._status_var = tk.StringVar(value="Draft")
        self._error_label: tk.Label | None = None

    def _build_field(self, container: tk.Frame, label: str, key: str) -> None:
        """Add a labeled text entry to the container."""
        row = tk.Frame(container, bg=COLORS["bg"])
        row.pack(fill=tk.X, pady=4)

        lbl = tk.Label(
            row,
            text=label,
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=(FONT_FAMILY, 10),
            width=12,
            anchor="w",
        )
        lbl.pack(side=tk.LEFT)

        entry = tk.Entry(
            row,
            font=(FONT_FAMILY, 10),
            bd=1,
            relief=tk.SOLID,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self._entries[key] = entry

    def _build_status_dropdown(self, container: tk.Frame) -> None:
        """Add a status dropdown."""
        row = tk.Frame(container, bg=COLORS["bg"])
        row.pack(fill=tk.X, pady=4)

        lbl = tk.Label(
            row,
            text="Status:",
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=(FONT_FAMILY, 10),
            width=12,
            anchor="w",
        )
        lbl.pack(side=tk.LEFT)

        combo = ttk.Combobox(
            row,
            textvariable=self._status_var,
            values=["Draft", "In Review", "Approved", "Archived"],
            state="readonly",
            font=(FONT_FAMILY, 10),
            width=20,
        )
        combo.pack(side=tk.LEFT)

    def _build_error_area(self, container: tk.Frame) -> None:
        """Add an error message label."""
        self._error_label = tk.Label(
            container,
            text="",
            bg=COLORS["bg"],
            fg=COLORS["danger"],
            font=(FONT_FAMILY, 9),
            anchor="w",
            wraplength=360,
        )
        self._error_label.pack(fill=tk.X, pady=(8, 0))

    def _show_error(self, message: str) -> None:
        if self._error_label:
            self._error_label.config(text=message)

    def _clear_error(self) -> None:
        if self._error_label:
            self._error_label.config(text="")

    def _get_entry(self, key: str) -> str:
        return self._entries[key].get()


# ------------------------------------------------------------------
# Add Version dialog
# ------------------------------------------------------------------

class AddVersionDialog(_BaseVersionDialog):
    """Dialog to create a new version at the end of the history."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, "Add New Version")

        container = tk.Frame(self, bg=COLORS["bg"], padx=24, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        heading = tk.Label(
            container,
            text="Create a New Document Version",
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=(FONT_FAMILY, 12, "bold"),
        )
        heading.pack(anchor="w", pady=(0, 12))

        self._build_field(container, "Version ID:", "version_id")
        self._build_field(container, "Title:", "title")
        self._build_field(container, "Author:", "author")
        self._build_field(container, "Summary:", "summary")
        self._build_status_dropdown(container)
        self._build_error_area(container)

        # Buttons
        btn_row = tk.Frame(container, bg=COLORS["bg"])
        btn_row.pack(fill=tk.X, pady=(16, 0))

        StyledButton(btn_row, text="Save", command=self._on_save, width=10).pack(side=tk.LEFT, padx=(0, 8))
        StyledButton(
            btn_row, text="Cancel", command=self.destroy,
            bg=COLORS["text_secondary"], hover_bg="#475569", width=10,
        ).pack(side=tk.LEFT)

        # Focus first field
        self._entries["version_id"].focus_set()

    def _on_save(self) -> None:
        self._clear_error()
        try:
            vid, ttl, aut, smr = validate_version_fields(
                self._get_entry("version_id"),
                self._get_entry("title"),
                self._get_entry("author"),
                self._get_entry("summary"),
            )
        except ValidationError as exc:
            self._show_error(str(exc))
            return

        self.result = {
            "version_id": vid,
            "title": ttl,
            "author": aut,
            "summary": smr,
            "status": self._status_var.get(),
        }
        self.destroy()


# ------------------------------------------------------------------
# Insert Version dialog (with position field)
# ------------------------------------------------------------------

class InsertVersionDialog(_BaseVersionDialog):
    """Dialog to insert a version at a specific position."""

    def __init__(self, parent: tk.Widget, max_position: int) -> None:
        super().__init__(parent, "Insert Version at Position")
        self._max_pos = max_position

        container = tk.Frame(self, bg=COLORS["bg"], padx=24, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        heading = tk.Label(
            container,
            text="Insert a Version at a Specific Position",
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=(FONT_FAMILY, 12, "bold"),
        )
        heading.pack(anchor="w", pady=(0, 4))

        hint = tk.Label(
            container,
            text=f"Valid positions: 0 to {max_position}",
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            font=(FONT_FAMILY, 9),
        )
        hint.pack(anchor="w", pady=(0, 12))

        self._build_field(container, "Position:", "position")
        self._build_field(container, "Version ID:", "version_id")
        self._build_field(container, "Title:", "title")
        self._build_field(container, "Author:", "author")
        self._build_field(container, "Summary:", "summary")
        self._build_status_dropdown(container)
        self._build_error_area(container)

        btn_row = tk.Frame(container, bg=COLORS["bg"])
        btn_row.pack(fill=tk.X, pady=(16, 0))

        StyledButton(btn_row, text="Insert", command=self._on_insert, width=10).pack(side=tk.LEFT, padx=(0, 8))
        StyledButton(
            btn_row, text="Cancel", command=self.destroy,
            bg=COLORS["text_secondary"], hover_bg="#475569", width=10,
        ).pack(side=tk.LEFT)

        self._entries["position"].focus_set()

    def _on_insert(self) -> None:
        self._clear_error()
        try:
            pos = validate_positive_integer(self._get_entry("position"), "Position")
            if pos < 0 or pos > self._max_pos:
                self._show_error(f"Position must be between 0 and {self._max_pos}.")
                return

            vid, ttl, aut, smr = validate_version_fields(
                self._get_entry("version_id"),
                self._get_entry("title"),
                self._get_entry("author"),
                self._get_entry("summary"),
            )
        except (ValidationError, ValueError) as exc:
            self._show_error(str(exc))
            return

        self.result = {
            "position": str(pos),
            "version_id": vid,
            "title": ttl,
            "author": aut,
            "summary": smr,
            "status": self._status_var.get(),
        }
        self.destroy()


# ------------------------------------------------------------------
# Search dialog
# ------------------------------------------------------------------

class SearchDialog(_BaseVersionDialog):
    """Dialog to search versions by ID or author."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, "Search Versions")

        container = tk.Frame(self, bg=COLORS["bg"], padx=24, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        heading = tk.Label(
            container,
            text="Search by Version ID or Author",
            bg=COLORS["bg"],
            fg=COLORS["text_primary"],
            font=(FONT_FAMILY, 12, "bold"),
        )
        heading.pack(anchor="w", pady=(0, 12))

        self._build_field(container, "Query:", "query")
        self._build_error_area(container)

        btn_row = tk.Frame(container, bg=COLORS["bg"])
        btn_row.pack(fill=tk.X, pady=(16, 0))

        StyledButton(btn_row, text="Search", command=self._on_search, width=10).pack(side=tk.LEFT, padx=(0, 8))
        StyledButton(
            btn_row, text="Cancel", command=self.destroy,
            bg=COLORS["text_secondary"], hover_bg="#475569", width=10,
        ).pack(side=tk.LEFT)

        self._entries["query"].focus_set()

    def _on_search(self) -> None:
        query = self._get_entry("query").strip()
        if not query:
            self._show_error("Please enter a search term.")
            return
        self.result = {"query": query}
        self.destroy()
