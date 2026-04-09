"""
Application bootstrap.

Initializes the service layer, loads sample data,
and launches the main window.
"""

import tkinter as tk

from src.services.document_timeline_service import DocumentTimelineService
from src.ui.main_window import MainWindow


class Application:
    """Top-level application coordinator."""

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._service = DocumentTimelineService()

        # Pre-load sample data so the user can explore immediately
        self._service.load_sample_data()

        self._window = MainWindow(self._root, self._service)

    def run(self) -> None:
        """Start the Tkinter main loop."""
        self._root.mainloop()
