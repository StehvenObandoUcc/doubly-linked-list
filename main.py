"""
DocuFlow Version Manager
========================
Entry point for the desktop application.
Manages the version history of technical documents
using a manually implemented doubly linked list.
"""

from src.app import Application


def main() -> None:
    """Launch the DocuFlow Version Manager application."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
