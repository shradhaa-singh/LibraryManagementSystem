import sqlite3
from contextlib import closing
from datetime import datetime, timedelta

from library_app.helpers import DATE_FORMAT, parse_positive_int


DATA = "Library.db"
FINE_PER_DAY = 5


def get_connection():
    return sqlite3.connect(DATA)


def initialize_database():
    with closing(get_connection()) as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS books(
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER CHECK(year >= 1500 AND year < 2100),
                price INTEGER CHECK(price > 0),
                available INTEGER CHECK(available >= 0)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS members(
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions(
                TransID INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                borrow_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT DEFAULT NULL,
                status TEXT NOT NULL CHECK(status IN ('Borrowed', 'Returned')),
                fine INTEGER DEFAULT 0,
                FOREIGN KEY(member_id) REFERENCES members(member_id),
                FOREIGN KEY(book_id) REFERENCES books(book_id)
            )
            """
        )

        columns = [row[1] for row in cur.execute("PRAGMA table_info(transactions)").fetchall()]
        if "due_date" not in columns:
            cur.execute("ALTER TABLE transactions ADD COLUMN due_date TEXT")
            cur.execute(
                """
                UPDATE transactions
                SET due_date = COALESCE(return_date, borrow_date)
                WHERE due_date IS NULL
                """
            )

        cur.execute(
            """
            UPDATE transactions
            SET status = CASE
                WHEN LOWER(status) = 'returned' THEN 'Returned'
                ELSE 'Borrowed'
            END
            """
        )
        con.commit()


def fetch_all_books():
    with closing(get_connection()) as con:
        return con.execute(
            "SELECT book_id, title, author, year, price, available FROM books ORDER BY book_id"
        ).fetchall()


def search_books(title=""):
    with closing(get_connection()) as con:
        return con.execute(
            """
            SELECT book_id, title, author, year, price, available
            FROM books
            WHERE title LIKE ?
            ORDER BY book_id
            """,
            (f"%{title.strip()}%",),
        ).fetchall()


def insert_book(title, author, year, price, available):
    with closing(get_connection()) as con:
        con.execute(
            """
            INSERT INTO books(title, author, year, price, available)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, author, year, price, available),
        )
        con.commit()


def update_book(book_id, title, author, year, price, available):
    with closing(get_connection()) as con:
        con.execute(
            """
            UPDATE books
            SET title = ?, author = ?, year = ?, price = ?, available = ?
            WHERE book_id = ?
            """,
            (title, author, year, price, available, book_id),
        )
        con.commit()


def delete_book(book_id):
    with closing(get_connection()) as con:
        active_txn = con.execute(
            """
            SELECT 1
            FROM transactions
            WHERE book_id = ? AND status = 'Borrowed'
            LIMIT 1
            """,
            (book_id,),
        ).fetchone()
        if active_txn:
            raise ValueError("This book is currently borrowed and cannot be deleted.")
        con.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        con.commit()


def fetch_all_members():
    with closing(get_connection()) as con:
        return con.execute(
            """
            SELECT member_id, name, email, address, phone
            FROM members
            ORDER BY member_id
            """
        ).fetchall()


def resolve_member_id(member_id_text="", member_name=""):
    member_id_text = member_id_text.strip()
    member_name = member_name.strip()

    with closing(get_connection()) as con:
        if member_id_text:
            member_id = parse_positive_int(member_id_text, "Member ID")
            member = con.execute(
                "SELECT member_id FROM members WHERE member_id = ?",
                (member_id,),
            ).fetchone()
            if not member:
                raise ValueError("Member ID does not exist.")
            return member_id

        if not member_name:
            raise ValueError("Enter either Member ID or an exact Member Name.")

        rows = con.execute(
            "SELECT member_id FROM members WHERE LOWER(name) = LOWER(?)",
            (member_name,),
        ).fetchall()
        if not rows:
            raise ValueError("Member name was not found.")
        if len(rows) > 1:
            raise ValueError("Multiple members matched this name. Use Member ID instead.")
        return rows[0][0]


def insert_member(name, email, address, phone):
    with closing(get_connection()) as con:
        con.execute(
            """
            INSERT INTO members(name, email, address, phone)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, address, phone),
        )
        con.commit()


def update_member(member_id, name, email, address, phone):
    with closing(get_connection()) as con:
        con.execute(
            """
            UPDATE members
            SET name = ?, email = ?, address = ?, phone = ?
            WHERE member_id = ?
            """,
            (name, email, address, phone, member_id),
        )
        con.commit()


def delete_member(member_id):
    with closing(get_connection()) as con:
        active_txn = con.execute(
            """
            SELECT 1
            FROM transactions
            WHERE member_id = ? AND status = 'Borrowed'
            LIMIT 1
            """,
            (member_id,),
        ).fetchone()
        if active_txn:
            raise ValueError("This member has an active borrowed book and cannot be deleted.")
        con.execute("DELETE FROM members WHERE member_id = ?", (member_id,))
        con.commit()


def fetch_transactions(status="All"):
    query = """
        SELECT TransID, member_id, book_id, borrow_date, due_date, return_date, status, fine
        FROM transactions
    """
    params = ()
    if status != "All":
        query += " WHERE status = ?"
        params = (status,)
    query += " ORDER BY TransID DESC"

    with closing(get_connection()) as con:
        return con.execute(query, params).fetchall()


def resolve_book_id(book_id_text="", book_title=""):
    book_id_text = book_id_text.strip()
    book_title = book_title.strip()

    with closing(get_connection()) as con:
        if book_id_text:
            book_id = parse_positive_int(book_id_text, "Book ID")
            book = con.execute(
                "SELECT book_id FROM books WHERE book_id = ?",
                (book_id,),
            ).fetchone()
            if not book:
                raise ValueError("Book ID does not exist.")
            return book_id

        if not book_title:
            raise ValueError("Enter either Book ID or an exact Book Title.")

        rows = con.execute(
            "SELECT book_id FROM books WHERE LOWER(title) = LOWER(?)",
            (book_title,),
        ).fetchall()
        if not rows:
            raise ValueError("Book title was not found.")
        if len(rows) > 1:
            raise ValueError("Multiple books matched this title. Use Book ID instead.")
        return rows[0][0]


def create_borrow_transaction(member_id, book_id, days_to_return):
    with closing(get_connection()) as con:
        cur = con.cursor()
        member = cur.execute(
            "SELECT member_id, name FROM members WHERE member_id = ?",
            (member_id,),
        ).fetchone()
        if not member:
            raise ValueError("Member ID does not exist.")

        book = cur.execute(
            "SELECT book_id, title, available FROM books WHERE book_id = ?",
            (book_id,),
        ).fetchone()
        if not book:
            raise ValueError("Book ID does not exist.")
        if book[2] <= 0:
            raise ValueError("This book is currently unavailable.")

        open_txn = cur.execute(
            """
            SELECT 1
            FROM transactions
            WHERE member_id = ? AND book_id = ? AND status = 'Borrowed'
            LIMIT 1
            """,
            (member_id, book_id),
        ).fetchone()
        if open_txn:
            raise ValueError("This member already has this book borrowed.")

        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=days_to_return)
        cur.execute(
            """
            INSERT INTO transactions(member_id, book_id, borrow_date, due_date, return_date, status, fine)
            VALUES (?, ?, ?, ?, NULL, 'Borrowed', 0)
            """,
            (
                member_id,
                book_id,
                borrow_date.strftime(DATE_FORMAT),
                due_date.strftime(DATE_FORMAT),
            ),
        )
        cur.execute(
            "UPDATE books SET available = available - 1 WHERE book_id = ?",
            (book_id,),
        )
        con.commit()


def complete_return_transaction(trans_id):
    with closing(get_connection()) as con:
        cur = con.cursor()
        txn = cur.execute(
            """
            SELECT TransID, book_id, due_date, status
            FROM transactions
            WHERE TransID = ?
            """,
            (trans_id,),
        ).fetchone()
        if not txn:
            raise ValueError("Transaction not found.")
        if txn[3] == "Returned":
            raise ValueError("This book has already been returned.")

        today = datetime.now()
        due_date = datetime.strptime(txn[2], DATE_FORMAT)
        late_days = max((today.date() - due_date.date()).days, 0)
        fine = late_days * FINE_PER_DAY

        cur.execute(
            """
            UPDATE transactions
            SET return_date = ?, status = 'Returned', fine = ?
            WHERE TransID = ?
            """,
            (today.strftime(DATE_FORMAT), fine, trans_id),
        )
        cur.execute(
            "UPDATE books SET available = available + 1 WHERE book_id = ?",
            (txn[1],),
        )
        con.commit()


def filter_reports(date_from="", date_to="", member_name="", book_title=""):
    query = """
        SELECT
            t.TransID,
            m.name,
            b.title,
            t.borrow_date,
            t.due_date,
            t.return_date,
            t.status,
            t.fine
        FROM transactions t
        LEFT JOIN members m ON t.member_id = m.member_id
        LEFT JOIN books b ON t.book_id = b.book_id
        WHERE (? = '' OR t.borrow_date >= ?)
          AND (? = '' OR t.borrow_date <= ?)
          AND (? = '' OR m.name LIKE ?)
          AND (? = '' OR b.title LIKE ?)
        ORDER BY t.TransID DESC
    """
    args = (
        date_from,
        date_from,
        date_to,
        date_to,
        member_name,
        f"%{member_name}%",
        book_title,
        f"%{book_title}%",
    )
    with closing(get_connection()) as con:
        return con.execute(query, args).fetchall()
