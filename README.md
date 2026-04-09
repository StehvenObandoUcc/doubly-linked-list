# DocuFlow Version Manager

A desktop application for managing the version history of technical documents, built as an academic project for a **Data Structures** workshop.

## Case Study

Technical teams frequently need to track the evolution of documents through multiple versions. **DocuFlow Version Manager** provides a navigable, ordered history where users can:

- Add new versions at the end of the timeline.
- Insert versions at any specific position.
- Delete versions by position or the currently selected version.
- Navigate forward and backward through the version chain.
- Search versions by ID or author.
- View the full history in ascending or descending order.

## How the Doubly Linked List Is Used

The core data structure is a **manually implemented doubly linked list** (`VersionHistory`), where each node (`VersionNode`) wraps a `DocumentVersion` and holds `prev` / `next` pointers.

```
 HEAD                                                  TAIL
  ↓                                                     ↓
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  v1.0   │⟷│  v1.1   │⟷│  v1.2   │⟷│  v2.0   │
│ (node)  │    │ (node)  │    │ (node)  │    │ (node)  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                    ↑
                 CURRENT
```

- **No Python native list** is used as the source of truth for the history.
- Navigation (`Previous` / `Next`) traverses the linked nodes via pointer references.
- Insertions and deletions correctly update `prev` and `next` on adjacent nodes.
- Temporary Python lists are generated only for UI rendering purposes.

## Project Structure

```
project/
│── main.py                          # Entry point
│── requirements.txt                 # Dependencies (none required)
│── README.md                        # This file
│
└── src/
    │── app.py                       # Application bootstrap
    │
    ├── models/
    │   └── document_version.py      # Domain entity
    │
    ├── data_structures/
    │   ├── version_node.py          # Doubly linked list node
    │   └── version_history.py       # Doubly linked list implementation
    │
    ├── services/
    │   └── version_history_service.py  # Business logic facade
    │
    ├── ui/
    │   ├── main_window.py           # Main application window
    │   ├── dialogs.py               # Modal input forms
    │   └── components.py            # Reusable UI widgets
    │
    └── utils/
        └── validators.py            # Input validation utilities
```

## Prerequisites

- **Python 3.11** or higher
- **Tkinter** (bundled with standard Python installations on Windows and macOS)

> On some Linux distributions you may need to install Tkinter separately:
> ```bash
> sudo apt-get install python3-tk
> ```

## How to Run

```bash
# From the project root directory:
python main.py
```

No additional dependencies are required — the application uses only the Python standard library.

## Sample Data

The application launches with four pre-loaded document versions so you can explore all features immediately:

| Version ID | Title                        | Author        | Status     |
|-----------|------------------------------|---------------|------------|
| v1.0      | Initial Architecture Proposal | Alice Chen    | Approved   |
| v1.1      | Architecture Review Notes     | Bob Martinez  | Approved   |
| v1.2      | Security Appendix Added       | Carol Nguyen  | In Review  |
| v2.0      | Major Redesign Draft          | Alice Chen    | Draft      |

## Architecture Overview

| Layer            | Responsibility                                    |
|-----------------|---------------------------------------------------|
| `models`        | Pure domain entities (no logic, no dependencies)  |
| `data_structures` | Doubly linked list implementation (pointer logic) |
| `services`      | Business rules, validation, coordination          |
| `ui`            | Graphical interface (Tkinter widgets)              |
| `utils`         | Small helper utilities (validators)                |

The UI communicates **only** with the service layer. The service layer is the only consumer of the linked list. This ensures clean separation of concerns.

## License

Academic project — free to use for educational purposes.
