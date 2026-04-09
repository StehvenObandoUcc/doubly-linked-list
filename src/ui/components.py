"""
Reusable UI components for DocuFlow Version Manager.
"""

import tkinter as tk
from tkinter import ttk


# ------------------------------------------------------------------
# Color palette
# ------------------------------------------------------------------

COLORS = {
    "bg": "#F5F7FA",
    "sidebar_bg": "#FFFFFF",
    "header_bg": "#2C3E7B",
    "header_fg": "#FFFFFF",
    "accent": "#3B82F6",
    "accent_hover": "#2563EB",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "success": "#10B981",
    "text_primary": "#1E293B",
    "text_secondary": "#64748B",
    "border": "#E2E8F0",
    "selected": "#DBEAFE",
    "current_marker": "#3B82F6",
    "card_bg": "#FFFFFF",
    "nav_btn": "#6366F1",
    "nav_btn_hover": "#4F46E5",
}

FONT_FAMILY = "Segoe UI"


# ------------------------------------------------------------------
# Header bar
# ------------------------------------------------------------------

class HeaderBar(tk.Frame):
    """Top banner displaying the application title."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=COLORS["header_bg"], height=60)
        self.pack_propagate(False)

        title_label = tk.Label(
            self,
            text="\U0001F4C4  DocuFlow Version Manager",
            bg=COLORS["header_bg"],
            fg=COLORS["header_fg"],
            font=(FONT_FAMILY, 16, "bold"),
            anchor="w",
            padx=20,
        )
        title_label.pack(fill=tk.X, expand=True)


# ------------------------------------------------------------------
# Styled button
# ------------------------------------------------------------------

class StyledButton(tk.Button):
    """Custom button with hover effects."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: object = None,
        bg: str = COLORS["accent"],
        fg: str = "#FFFFFF",
        hover_bg: str = COLORS["accent_hover"],
        width: int = 16,
        **kwargs: object,
    ) -> None:
        super().__init__(
            parent,
            text=text,
            command=command,  # type: ignore[arg-type]
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            font=(FONT_FAMILY, 10),
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            width=width,
            pady=6,
            **kwargs,  # type: ignore[arg-type]
        )
        self._bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        self.config(bg=self._hover_bg)

    def _on_leave(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        self.config(bg=self._bg)


# ------------------------------------------------------------------
# Status bar (footer)
# ------------------------------------------------------------------

class StatusBar(tk.Frame):
    """Footer bar that shows contextual messages."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=COLORS["border"], height=28)
        self.pack_propagate(False)

        self._label = tk.Label(
            self,
            text="Ready",
            bg=COLORS["border"],
            fg=COLORS["text_secondary"],
            font=(FONT_FAMILY, 9),
            anchor="w",
            padx=12,
        )
        self._label.pack(fill=tk.X, expand=True)

    def set_message(self, message: str, kind: str = "info") -> None:
        """Display a message. *kind* can be 'info', 'success', or 'error'."""
        color_map = {
            "info": COLORS["text_secondary"],
            "success": COLORS["success"],
            "error": COLORS["danger"],
        }
        self._label.config(text=message, fg=color_map.get(kind, COLORS["text_secondary"]))


# ------------------------------------------------------------------
# Detail card — displays version info
# ------------------------------------------------------------------

class VersionDetailCard(tk.Frame):
    """Panel that displays the full details of a single document version."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=COLORS["card_bg"], bd=1, relief=tk.SOLID, highlightbackground=COLORS["border"])

        self._fields: dict[str, tk.Label] = {}

        header = tk.Label(
            self,
            text="Version Details",
            bg=COLORS["card_bg"],
            fg=COLORS["text_primary"],
            font=(FONT_FAMILY, 13, "bold"),
            anchor="w",
        )
        header.pack(fill=tk.X, padx=16, pady=(16, 8))

        separator = tk.Frame(self, bg=COLORS["border"], height=1)
        separator.pack(fill=tk.X, padx=16, pady=(0, 8))

        for field_name in ("Version ID", "Title", "Author", "Status", "Created At", "Summary"):
            row = tk.Frame(self, bg=COLORS["card_bg"])
            row.pack(fill=tk.X, padx=16, pady=3)

            lbl = tk.Label(
                row,
                text=f"{field_name}:",
                bg=COLORS["card_bg"],
                fg=COLORS["text_secondary"],
                font=(FONT_FAMILY, 10, "bold"),
                width=12,
                anchor="w",
            )
            lbl.pack(side=tk.LEFT)

            value_lbl = tk.Label(
                row,
                text="—",
                bg=COLORS["card_bg"],
                fg=COLORS["text_primary"],
                font=(FONT_FAMILY, 10),
                anchor="w",
                wraplength=380,
                justify=tk.LEFT,
            )
            value_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._fields[field_name] = value_lbl

    def display(self, data: dict[str, str] | None) -> None:
        """Populate the card with version data or clear it."""
        if data is None:
            for lbl in self._fields.values():
                lbl.config(text="—")
            return

        mapping = {
            "Version ID": "version_id",
            "Title": "title",
            "Author": "author",
            "Status": "status",
            "Created At": "created_at",
            "Summary": "summary",
        }
        for display_name, key in mapping.items():
            self._fields[display_name].config(text=data.get(key, "—"))
