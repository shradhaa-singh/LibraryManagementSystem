# Library Management System

A desktop library management application built with Python, Tkinter, and SQLite.

This project provides a simple GUI to manage:
- books
- members
- borrowing and returning
- transaction reports

The application stores data locally in `Library.db` and runs as a standard Python desktop app.

## Features

- Add, update, delete, and search books
- Add, update, and delete members
- Borrow books using member ID or exact member name
- Borrow books using book ID or exact book title
- Automatically decrease available stock when a book is borrowed
- Return books from the transactions table
- Automatically restore available stock when a book is returned
- Automatically calculate overdue fines
- Filter transactions by status
- Generate report data in table and text format

## Tech Stack

- Python 3
- Tkinter / ttk
- SQLite3

## Project Structure

```text
LibraryManagementSystem/
├── LIBRARY.py
├── Library.db
├── README.md
└── library_app/
    ├── __init__.py
    ├── database.py
    ├── helpers.py
    └── ui.py
```

## File Roles

- `LIBRARY.py`
  Main entry point. Run this file to start the app.

- `library_app/ui.py`
  Tkinter user interface, tabs, widgets, button callbacks, and table refresh logic.

- `library_app/database.py`
  SQLite setup and database operations for books, members, transactions, and reports.

- `library_app/helpers.py`
  Shared helper functions such as validation, selected-row handling, and report text formatting.

## How To Run

1. Make sure Python 3 is installed.
2. Open the project folder in terminal.
3. Run:

```bash
python3 LIBRARY.py
```

Do not run `library_app/ui.py` directly unless you intentionally add a separate standalone runner for it.

## How The App Works

### Books Tab

- Search books by title
- Show all books
- Add a new book
- Update selected book details
- Delete a selected book

### Members Tab

- Add a member
- Update selected member details
- Delete a selected member

### Transactions Tab

- Borrow a book
- Return a selected borrowed book
- View all transactions
- Filter transactions by `All`, `Borrowed`, or `Returned`

### Reports Tab

- Filter by date range
- Filter by member name
- Filter by book title
- View report records in a table
- View the same report in text format

## Database Tables

The application creates these tables automatically if they do not already exist:

- `books`
- `members`
- `transactions`

### `books`

- `book_id`
- `title`
- `author`
- `year`
- `price`
- `available`

### `members`

- `member_id`
- `name`
- `email`
- `address`
- `phone`

### `transactions`

- `TransID`
- `member_id`
- `book_id`
- `borrow_date`
- `due_date`
- `return_date`
- `status`
- `fine`

## Validation And Rules

- Book year must be between `1500` and `2099`
- Price must be greater than `0`
- Available copies cannot be negative
- A borrowed book cannot be deleted while still issued
- A member with an active borrowed book cannot be deleted
- A book cannot be borrowed if no copies are available
- The same member cannot borrow the same book again until it is returned
- Fine is calculated when the book is returned

## Notes

- Data is stored in the local SQLite file `Library.db`
- If `Library.db` already exists, the app reuses it
- The app auto-creates missing tables on startup
- The UI uses standard `ttk` widgets for a simple desktop look

## Known Limitations

- Member name and book title matching in the borrow section is exact, not partial
- If multiple members have the same exact name, the app asks you to use member ID
- If multiple books have the same exact title, the app asks you to use book ID
- There is no login system
- There is no export to PDF or Excel yet

## Future Improvements

- Add search for members
- Add search by author
- Add export for reports
- Add issue history by member
- Add dashboard statistics
- Add form reset buttons

## Author

Shradha Singh
