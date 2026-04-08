import tkinter as tk
from datetime import datetime


DATE_FORMAT = "%Y-%m-%d"


def parse_positive_int(value, field_name, allow_zero=False):
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a whole number.") from exc

    if allow_zero:
        if number < 0:
            raise ValueError(f"{field_name} cannot be negative.")
    elif number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return number


def parse_date(value, field_name):
    if not value.strip():
        return ""
    try:
        datetime.strptime(value.strip(), DATE_FORMAT)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be in YYYY-MM-DD format.") from exc
    return value.strip()


def selected_row(tree):
    selected = tree.selection()
    if not selected:
        raise ValueError("Select a row first.")
    return tree.item(selected[0])["values"]


def clear_entries(entries):
    for entry in entries:
        entry.delete(0, tk.END)


def fill_entries_from_row(event, tree, entries):
    selected = tree.selection()
    if not selected:
        return
    values = tree.item(selected[0])["values"]
    for entry, value in zip(entries, values[1:]):
        entry.delete(0, tk.END)
        entry.insert(0, value)


def build_report_text(records):
    if not records:
        return "No records found."

    lines = []
    for trans_id, member, book, borrow_date, due_date, return_date, status, fine in records:
        lines.append(
            f"TransID: {trans_id} | Member: {member or '-'} | Book: {book or '-'} | "
            f"Borrowed: {borrow_date} | Due: {due_date} | Returned: {return_date or '-'} | "
            f"Status: {status} | Fine: Rs. {fine}"
        )
    return "\n".join(lines)
