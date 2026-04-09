"""
MainWindow — primary desktop window for DocuFlow Version Manager.

Layout:
  ┌──────────────── Header ─────────────────┐
  │  📄 DocuFlow Version Manager             │
  ├────────────┬────────────────────────────┤
  │  Sidebar   │   Main Panel               │
  │  (history  │   ┌────────────────────┐   │
  │   list)    │   │  Version Detail     │   │
  │            │   │  Card               │   │
  │            │   └────────────────────┘   │
  │            │   ┌─ Navigation ──────┐   │
  │            │   │ ◀ Prev   Next ▶   │   │
  │            │   └───────────────────┘   │
  │            │   ┌─ Actions ─────────┐   │
  │            │   │ Add  Insert  Del  │   │
  │            │   └───────────────────┘   │
  ├────────────┴────────────────────────────┤
  │  Status Bar                              │
  └──────────────────────────────────────────┘
"""

import tkinter as tk
from tkinter import messagebox
from dataclasses import asdict

from src.services.document_timeline_service import DocumentTimelineService
from src.models.document_version import DocumentVersion
from src.utils.validators import ValidationError
from src.ui.components import (
    COLORS,
    FONT_FAMILY,
    HeaderBar,
    StyledButton,
    StatusBar,
    VersionDetailCard,
)
from src.ui.dialogs import AddVersionDialog, InsertVersionDialog, SearchDialog


class MainWindow:
    """Main application window."""

    def __init__(self, root: tk.Tk, service: DocumentTimelineService) -> None:
        self._root = root
        self._service = service

        # Drag-and-drop state
        self._drag_active: bool = False
        self._drag_start_index: int = -1
        self._drag_current_index: int = -1

        self._configure_root()
        self._build_ui()
        self._refresh_sidebar()

    # ------------------------------------------------------------------
    # Root window configuration
    # ------------------------------------------------------------------

    def _configure_root(self) -> None:
        self._root.title("DocuFlow Version Manager")
        self._root.geometry("960x640")
        self._root.minsize(800, 520)
        self._root.configure(bg=COLORS["bg"])

        # Try to set the window icon gracefully
        try:
            self._root.iconbitmap(default="")
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Header
        self._header = HeaderBar(self._root)
        self._header.pack(fill=tk.X)

        # Body (sidebar + main panel)
        body = tk.Frame(self._root, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(body)
        self._build_main_panel(body)

        # Status bar
        self._status_bar = StatusBar(self._root)
        self._status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ── Sidebar ──────────────────────────────────────────────────────

    def _build_sidebar(self, parent: tk.Frame) -> None:
        sidebar = tk.Frame(parent, bg=COLORS["sidebar_bg"], width=280, bd=0)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Sidebar header
        sidebar_title = tk.Label(
            sidebar,
            text="Version History",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["text_primary"],
            font=(FONT_FAMILY, 12, "bold"),
            anchor="w",
            padx=14,
        )
        sidebar_title.pack(fill=tk.X, pady=(14, 4))

        # Order toggle
        order_frame = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        order_frame.pack(fill=tk.X, padx=14, pady=(0, 6))

        self._order_var = tk.StringVar(value="asc")
        tk.Radiobutton(
            order_frame, text="Ascending", variable=self._order_var,
            value="asc", bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"],
            font=(FONT_FAMILY, 9), selectcolor=COLORS["sidebar_bg"],
            activebackground=COLORS["sidebar_bg"],
            command=self._refresh_sidebar,
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            order_frame, text="Descending", variable=self._order_var,
            value="desc", bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"],
            font=(FONT_FAMILY, 9), selectcolor=COLORS["sidebar_bg"],
            activebackground=COLORS["sidebar_bg"],
            command=self._refresh_sidebar,
        ).pack(side=tk.LEFT, padx=(8, 0))

        # Separator
        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill=tk.X, padx=14)

        # Listbox + scrollbar
        list_frame = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self._version_listbox = tk.Listbox(
            list_frame,
            bg=COLORS["sidebar_bg"],
            fg=COLORS["text_primary"],
            font=(FONT_FAMILY, 10),
            selectbackground=COLORS["selected"],
            selectforeground=COLORS["text_primary"],
            activestyle="none",
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self._version_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._version_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._version_listbox.bind("<<ListboxSelect>>", self._on_sidebar_select)

        # Drag-and-drop bindings
        self._version_listbox.bind("<ButtonPress-1>", self._on_drag_start)
        self._version_listbox.bind("<B1-Motion>", self._on_drag_motion)
        self._version_listbox.bind("<ButtonRelease-1>", self._on_drag_drop)

        # Drag indicator — a thin colored line drawn between items
        self._drag_indicator = tk.Frame(sidebar, bg=COLORS["accent"], height=3)
        # (packed/placed dynamically during drag)

        # Drag hint label
        self._drag_hint = tk.Label(
            sidebar,
            text="\u2195  Drag to reorder",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["text_secondary"],
            font=(FONT_FAMILY, 8),
            anchor="center",
        )
        self._drag_hint.pack(fill=tk.X, padx=14, pady=(2, 0))

        # Sidebar count label
        self._count_label = tk.Label(
            sidebar,
            text="0 versions",
            bg=COLORS["sidebar_bg"],
            fg=COLORS["text_secondary"],
            font=(FONT_FAMILY, 9),
            anchor="w",
            padx=14,
        )
        self._count_label.pack(fill=tk.X, pady=(0, 10))

    # ── Main panel ───────────────────────────────────────────────────

    def _build_main_panel(self, parent: tk.Frame) -> None:
        panel = tk.Frame(parent, bg=COLORS["bg"])
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Detail card
        self._detail_card = VersionDetailCard(panel)
        self._detail_card.pack(fill=tk.X, pady=(0, 16))

        # Navigation buttons
        nav_frame = tk.Frame(panel, bg=COLORS["bg"])
        nav_frame.pack(fill=tk.X, pady=(0, 12))

        nav_label = tk.Label(
            nav_frame,
            text="Navigation",
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            font=(FONT_FAMILY, 10, "bold"),
        )
        nav_label.pack(anchor="w", pady=(0, 6))

        nav_btn_row = tk.Frame(nav_frame, bg=COLORS["bg"])
        nav_btn_row.pack(fill=tk.X)

        StyledButton(
            nav_btn_row, text="\u25C0  Previous", command=self._on_previous,
            bg=COLORS["nav_btn"], hover_bg=COLORS["nav_btn_hover"], width=14,
        ).pack(side=tk.LEFT, padx=(0, 8))

        StyledButton(
            nav_btn_row, text="Next  \u25B6", command=self._on_next,
            bg=COLORS["nav_btn"], hover_bg=COLORS["nav_btn_hover"], width=14,
        ).pack(side=tk.LEFT)

        # Action buttons
        action_frame = tk.Frame(panel, bg=COLORS["bg"])
        action_frame.pack(fill=tk.X, pady=(0, 12))

        action_label = tk.Label(
            action_frame,
            text="Actions",
            bg=COLORS["bg"],
            fg=COLORS["text_secondary"],
            font=(FONT_FAMILY, 10, "bold"),
        )
        action_label.pack(anchor="w", pady=(0, 6))

        row1 = tk.Frame(action_frame, bg=COLORS["bg"])
        row1.pack(fill=tk.X, pady=(0, 6))

        StyledButton(row1, text="\u2795  Add Version", command=self._on_add_version, width=18).pack(side=tk.LEFT, padx=(0, 8))
        StyledButton(row1, text="\U0001F4CD  Insert at Position", command=self._on_insert_version, width=18).pack(side=tk.LEFT, padx=(0, 8))
        StyledButton(row1, text="\U0001F50D  Search", command=self._on_search, width=18).pack(side=tk.LEFT)

        row2 = tk.Frame(action_frame, bg=COLORS["bg"])
        row2.pack(fill=tk.X)

        StyledButton(
            row2, text="\u274C  Delete Selected", command=self._on_delete_selected,
            bg=COLORS["danger"], hover_bg=COLORS["danger_hover"], width=18,
        ).pack(side=tk.LEFT, padx=(0, 8))

        StyledButton(
            row2, text="\U0001F5D1  Delete Current", command=self._on_delete_current,
            bg=COLORS["danger"], hover_bg=COLORS["danger_hover"], width=18,
        ).pack(side=tk.LEFT, padx=(0, 8))

        StyledButton(
            row2, text="\U0001F504  Refresh", command=self._on_refresh,
            bg=COLORS["success"], hover_bg="#059669", width=18,
        ).pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Sidebar refresh
    # ------------------------------------------------------------------

    def _refresh_sidebar(self) -> None:
        """Rebuild the sidebar listbox from the linked list."""
        self._version_listbox.delete(0, tk.END)

        if self._order_var.get() == "desc":
            versions = self._service.get_all_versions_backward()
        else:
            versions = self._service.get_all_versions_forward()

        for v in versions:
            self._version_listbox.insert(tk.END, f"  {v.version_id}  —  {v.title}")

        # Highlight current version
        current_idx = self._service.current_index
        if current_idx >= 0:
            display_idx = current_idx if self._order_var.get() == "asc" else (self._service.timeline_size - 1 - current_idx)
            if 0 <= display_idx < self._version_listbox.size():
                self._version_listbox.selection_set(display_idx)
                self._version_listbox.see(display_idx)

        self._count_label.config(text=f"{self._service.timeline_size} version(s)")
        self._update_detail_card()

    def _update_detail_card(self) -> None:
        """Update the detail card with the current version data."""
        current = self._service.get_current_version_data()
        if current is not None:
            self._detail_card.display(asdict(current))
        else:
            self._detail_card.display(None)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_sidebar_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        # Ignore selection events triggered during a drag
        if self._drag_active:
            return

        selection = self._version_listbox.curselection()
        if not selection:
            return
        display_idx = selection[0]

        # Translate display index back to linked-list index
        if self._order_var.get() == "desc":
            real_idx = self._service.timeline_size - 1 - display_idx
        else:
            real_idx = display_idx

        try:
            self._service.select_version_at(real_idx)
        except IndexError:
            return
        self._update_detail_card()
        self._status_bar.set_message(f"Selected version at position {real_idx}.", "info")

    # ------------------------------------------------------------------
    # Drag-and-drop handlers
    # ------------------------------------------------------------------

    def _display_to_real_index(self, display_idx: int) -> int:
        """Convert a listbox display index to the real linked-list index."""
        if self._order_var.get() == "desc":
            return self._service.timeline_size - 1 - display_idx
        return display_idx

    def _real_to_display_index(self, real_idx: int) -> int:
        """Convert a real linked-list index to the listbox display index."""
        if self._order_var.get() == "desc":
            return self._service.timeline_size - 1 - real_idx
        return real_idx

    def _on_drag_start(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Record the item under the cursor when the user presses the mouse."""
        index = self._version_listbox.nearest(event.y)
        if index < 0 or index >= self._version_listbox.size():
            return
        self._drag_start_index = index
        self._drag_current_index = index
        self._drag_active = False  # not yet — activated on first motion

    def _on_drag_motion(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        """Show a visual indicator line at the drop target while dragging."""
        if self._drag_start_index < 0:
            return

        target = self._version_listbox.nearest(event.y)
        if target < 0:
            target = 0
        if target >= self._version_listbox.size():
            target = self._version_listbox.size() - 1

        # Activate drag mode on first significant motion
        if not self._drag_active and target != self._drag_start_index:
            self._drag_active = True
            self._version_listbox.config(cursor="fleur")  # move cursor

        if not self._drag_active:
            return

        self._drag_current_index = target

        # Position the indicator line
        try:
            bbox = self._version_listbox.bbox(target)
        except Exception:
            bbox = None

        if bbox is not None:
            # bbox = (x, y, width, height) relative to the listbox
            listbox_x = self._version_listbox.winfo_rootx() - self._drag_indicator.master.winfo_rootx()
            listbox_y = self._version_listbox.winfo_rooty() - self._drag_indicator.master.winfo_rooty()

            # Put the indicator above or below the target item
            if target > self._drag_start_index:
                y_pos = listbox_y + bbox[1] + bbox[3]  # below target
            else:
                y_pos = listbox_y + bbox[1]  # above target

            self._drag_indicator.place(
                x=listbox_x + 4,
                y=y_pos,
                width=self._version_listbox.winfo_width() - 8,
                height=3,
            )
            self._drag_indicator.lift()
        else:
            self._drag_indicator.place_forget()

        # Highlight the target row
        self._version_listbox.selection_clear(0, tk.END)
        self._version_listbox.selection_set(self._drag_start_index)

        self._status_bar.set_message(
            f"Dragging from position {self._drag_start_index} → {target}", "info"
        )

    def _on_drag_drop(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        """Finalize the drag: move the version in the linked list."""
        # Hide the indicator
        self._drag_indicator.place_forget()
        self._version_listbox.config(cursor="")

        if not self._drag_active or self._drag_start_index < 0:
            self._drag_active = False
            self._drag_start_index = -1
            return

        from_display = self._drag_start_index
        to_display = self._drag_current_index

        # Reset state
        self._drag_active = False
        self._drag_start_index = -1
        self._drag_current_index = -1

        if from_display == to_display:
            return

        # Convert to real linked-list indices
        from_real = self._display_to_real_index(from_display)
        to_real = self._display_to_real_index(to_display)

        try:
            self._service.reorder_version(from_real, to_real)
            self._refresh_sidebar()
            self._status_bar.set_message(
                f"Moved version from position {from_real} to {to_real}.", "success"
            )
        except IndexError as exc:
            self._status_bar.set_message(str(exc), "error")

    def _on_previous(self) -> None:
        if self._service.go_to_previous_version():
            self._refresh_sidebar()
            self._status_bar.set_message("Moved to previous version.", "success")
        else:
            self._status_bar.set_message("Already at the first version.", "error")

    def _on_next(self) -> None:
        if self._service.go_to_next_version():
            self._refresh_sidebar()
            self._status_bar.set_message("Moved to next version.", "success")
        else:
            self._status_bar.set_message("Already at the last version.", "error")

    def _on_add_version(self) -> None:
        dialog = AddVersionDialog(self._root)
        self._root.wait_window(dialog)

        if dialog.result is None:
            return

        try:
            version = self._service.create_version(**dialog.result)
            self._refresh_sidebar()
            self._status_bar.set_message(f"Version '{version.version_id}' added successfully.", "success")
        except (ValidationError, IndexError) as exc:
            messagebox.showerror("Error", str(exc))
            self._status_bar.set_message("Failed to add version.", "error")

    def _on_insert_version(self) -> None:
        dialog = InsertVersionDialog(self._root, self._service.timeline_size)
        self._root.wait_window(dialog)

        if dialog.result is None:
            return

        try:
            data = dialog.result
            pos = int(data.pop("position"))
            version = self._service.insert_version(pos, **data)
            self._refresh_sidebar()
            self._status_bar.set_message(f"Version '{version.version_id}' inserted at position {pos}.", "success")
        except (ValidationError, IndexError) as exc:
            messagebox.showerror("Error", str(exc))
            self._status_bar.set_message("Failed to insert version.", "error")

    def _on_delete_selected(self) -> None:
        selection = self._version_listbox.curselection()
        if not selection:
            self._status_bar.set_message("No version selected in the sidebar.", "error")
            return

        display_idx = selection[0]
        if self._order_var.get() == "desc":
            real_idx = self._service.timeline_size - 1 - display_idx
        else:
            real_idx = display_idx

        if not messagebox.askyesno("Confirm Deletion", f"Delete the version at position {real_idx}?"):
            return

        try:
            removed = self._service.delete_version_at(real_idx)
            self._refresh_sidebar()
            self._status_bar.set_message(f"Version '{removed.version_id}' deleted.", "success")
        except IndexError as exc:
            messagebox.showerror("Error", str(exc))
            self._status_bar.set_message("Failed to delete version.", "error")

    def _on_delete_current(self) -> None:
        current = self._service.get_current_version_data()
        if current is None:
            self._status_bar.set_message("No current version to delete.", "error")
            return

        if not messagebox.askyesno("Confirm Deletion", f"Delete the current version '{current.version_id}'?"):
            return

        try:
            removed = self._service.delete_current_version()
            self._refresh_sidebar()
            self._status_bar.set_message(f"Version '{removed.version_id}' deleted.", "success")
        except IndexError as exc:
            messagebox.showerror("Error", str(exc))
            self._status_bar.set_message("Failed to delete version.", "error")

    def _on_search(self) -> None:
        dialog = SearchDialog(self._root)
        self._root.wait_window(dialog)

        if dialog.result is None:
            return

        query = dialog.result["query"]
        results = self._service.search_versions(query)

        if not results:
            messagebox.showinfo("Search Results", f"No versions found for '{query}'.")
            self._status_bar.set_message(f"Search: no results for '{query}'.", "info")
            return

        # Build a readable message
        lines = [f"Found {len(results)} result(s) for '{query}':\n"]
        for v in results:
            lines.append(f"  • [{v.version_id}] {v.title} by {v.author} ({v.status})")

        messagebox.showinfo("Search Results", "\n".join(lines))
        self._status_bar.set_message(f"Search: {len(results)} result(s) for '{query}'.", "success")

    def _on_refresh(self) -> None:
        self._refresh_sidebar()
        self._status_bar.set_message("View refreshed.", "success")
