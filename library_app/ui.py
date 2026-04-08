import tkinter as tk
from tkinter import messagebox, ttk

from library_app.database import (
    create_borrow_transaction,
    delete_book,
    delete_member,
    fetch_all_books,
    fetch_all_members,
    fetch_transactions,
    filter_reports,
    initialize_database,
    insert_book,
    insert_member,
    resolve_book_id,
    resolve_member_id,
    search_books,
    update_book,
    update_member,
    complete_return_transaction,
)
from library_app.helpers import (
    build_report_text,
    clear_entries,
    fill_entries_from_row,
    parse_date,
    parse_positive_int,
    selected_row,
)


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1250x700")
        self.root.minsize(1100, 650)

        initialize_database()
        self._configure_style()
        self._build_ui()
        self.refresh_books()
        self.refresh_members()
        self.refresh_transactions()
        self.generate_report_callback()

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=(16, 8), font=("TkDefaultFont", 10, "bold"))
        style.configure("TLabelFrame", padding=8)
        style.configure("Treeview", rowheight=24)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 10, "bold"))

    def _create_labeled_entry(self, parent, text, row, column, width=24):
        ttk.Label(parent, text=text).grid(row=row, column=column, padx=6, pady=6, sticky="e")
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=column + 1, padx=6, pady=6, sticky="we")
        return entry

    def _build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.books_tab = ttk.Frame(notebook, padding=10)
        self.members_tab = ttk.Frame(notebook, padding=10)
        self.transactions_tab = ttk.Frame(notebook, padding=10)
        self.reports_tab = ttk.Frame(notebook, padding=10)

        notebook.add(self.books_tab, text="Books")
        notebook.add(self.members_tab, text="Members")
        notebook.add(self.transactions_tab, text="Transactions")
        notebook.add(self.reports_tab, text="Reports")

        self._build_books_tab()
        self._build_members_tab()
        self._build_transactions_tab()
        self._build_reports_tab()

    def _build_books_tab(self):
        controls = ttk.LabelFrame(self.books_tab, text="Search And Manage Books")
        controls.pack(fill="x", pady=(0, 10))
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        self.search_entry = self._create_labeled_entry(controls, "Title", 0, 0, 30)
        ttk.Button(controls, text="Search", command=lambda: self.refresh_books(self.search_entry.get())).grid(
            row=0, column=2, padx=6, pady=6
        )
        ttk.Button(controls, text="Show All", command=self.refresh_books).grid(row=0, column=3, padx=6, pady=6, sticky="w")

        self.title_entry = self._create_labeled_entry(controls, "Title", 1, 0, 30)
        self.author_entry = self._create_labeled_entry(controls, "Author", 1, 2, 30)
        self.year_entry = self._create_labeled_entry(controls, "Year", 2, 0, 30)
        self.price_entry = self._create_labeled_entry(controls, "Price", 2, 2, 30)
        self.available_entry = self._create_labeled_entry(controls, "Available Copies", 3, 0, 30)

        button_row = ttk.Frame(controls)
        button_row.grid(row=4, column=0, columnspan=4, pady=(6, 0), sticky="w")
        ttk.Button(button_row, text="Add Book", command=self.add_book_callback).pack(side="left", padx=4)
        ttk.Button(button_row, text="Update Book", command=self.update_book_callback).pack(side="left", padx=4)
        ttk.Button(button_row, text="Delete Book", command=self.delete_book_callback).pack(side="left", padx=4)

        table = ttk.LabelFrame(self.books_tab, text="Book List")
        table.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table)
        scrollbar.pack(side="right", fill="y")
        self.tree1 = ttk.Treeview(
            table,
            columns=("ID", "Title", "Author", "Year", "Price", "Available"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        for col, width in [("ID", 70), ("Title", 260), ("Author", 220), ("Year", 100), ("Price", 100), ("Available", 120)]:
            self.tree1.heading(col, text=col)
            self.tree1.column(col, width=width, anchor="center")
        self.tree1.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree1.yview)
        self.tree1.bind(
            "<<TreeviewSelect>>",
            lambda event: fill_entries_from_row(
                event,
                self.tree1,
                [self.title_entry, self.author_entry, self.year_entry, self.price_entry, self.available_entry],
            ),
        )

    def _build_members_tab(self):
        controls = ttk.LabelFrame(self.members_tab, text="Manage Members")
        controls.pack(fill="x", pady=(0, 10))
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        self.name_entry = self._create_labeled_entry(controls, "Name", 0, 0, 32)
        self.email_entry = self._create_labeled_entry(controls, "Email", 0, 2, 32)
        self.add_entry = self._create_labeled_entry(controls, "Address", 1, 0, 32)
        self.ph_entry = self._create_labeled_entry(controls, "Phone", 1, 2, 32)

        button_row = ttk.Frame(controls)
        button_row.grid(row=2, column=0, columnspan=4, pady=(6, 0), sticky="w")
        ttk.Button(button_row, text="Add Member", command=self.add_member_callback).pack(side="left", padx=4)
        ttk.Button(button_row, text="Update Member", command=self.update_member_callback).pack(side="left", padx=4)
        ttk.Button(button_row, text="Delete Member", command=self.delete_member_callback).pack(side="left", padx=4)

        table = ttk.LabelFrame(self.members_tab, text="Member List")
        table.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table)
        scrollbar.pack(side="right", fill="y")
        self.tree2 = ttk.Treeview(
            table,
            columns=("ID", "Name", "Email", "Address", "Phone"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        for col, width in [("ID", 70), ("Name", 180), ("Email", 260), ("Address", 300), ("Phone", 160)]:
            self.tree2.heading(col, text=col)
            self.tree2.column(col, width=width, anchor="center")
        self.tree2.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree2.yview)
        self.tree2.bind(
            "<<TreeviewSelect>>",
            lambda event: fill_entries_from_row(
                event,
                self.tree2,
                [self.name_entry, self.email_entry, self.add_entry, self.ph_entry],
            ),
        )

    def _build_transactions_tab(self):
        controls = ttk.LabelFrame(self.transactions_tab, text="Issue And Return History")
        controls.pack(fill="x", pady=(0, 10))
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)
        controls.columnconfigure(5, weight=1)

        self.mem_entry = self._create_labeled_entry(controls, "Member Name", 0, 0, 22)
        self.memID_entry = self._create_labeled_entry(controls, "Member ID", 1, 0, 22)
        self.bookT_entry = self._create_labeled_entry(controls, "Book Title", 0, 2, 22)
        self.bookID_entry = self._create_labeled_entry(controls, "Book ID", 1, 2, 22)
        self.returnDay_entry = self._create_labeled_entry(controls, "Days To Return", 1, 4, 22)

        ttk.Label(controls, text="Status").grid(row=0, column=4, padx=6, pady=6, sticky="e")
        self.status_var = tk.StringVar(value="All")
        self.status_combobox = ttk.Combobox(
            controls,
            textvariable=self.status_var,
            values=("All", "Borrowed", "Returned"),
            state="readonly",
            width=20,
        )
        self.status_combobox.grid(row=0, column=5, padx=6, pady=6, sticky="w")

        button_row = ttk.Frame(controls)
        button_row.grid(row=2, column=0, columnspan=6, pady=(6, 0), sticky="w")
        ttk.Button(button_row, text="Apply Filter", command=self.refresh_transactions).pack(side="left", padx=4)
        ttk.Button(button_row, text="Borrow Book", command=self.borrow_book_callback).pack(side="left", padx=4)
        ttk.Button(button_row, text="Return Book", command=self.return_book_callback).pack(side="left", padx=4)

        table = ttk.LabelFrame(self.transactions_tab, text="Transaction List")
        table.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table)
        scrollbar.pack(side="right", fill="y")
        self.tree3 = ttk.Treeview(
            table,
            columns=("TransID", "MemberID", "BookID", "BorrowDate", "DueDate", "ReturnDate", "Status", "Fine"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        for col, width in [
            ("TransID", 90),
            ("MemberID", 110),
            ("BookID", 100),
            ("BorrowDate", 120),
            ("DueDate", 120),
            ("ReturnDate", 120),
            ("Status", 100),
            ("Fine", 80),
        ]:
            self.tree3.heading(col, text=col)
            self.tree3.column(col, width=width, anchor="center")
        self.tree3.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree3.yview)

    def _build_reports_tab(self):
        controls = ttk.LabelFrame(self.reports_tab, text="Report Filters")
        controls.pack(fill="x", pady=(0, 10))
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        self.entry_r_datefrom = self._create_labeled_entry(controls, "Date From", 0, 0, 22)
        self.entry_r_dateto = self._create_labeled_entry(controls, "Date To", 0, 2, 22)
        self.entry_r_membername = self._create_labeled_entry(controls, "Member Name", 1, 0, 22)
        self.entry_r_booktitle = self._create_labeled_entry(controls, "Book Title", 1, 2, 22)
        ttk.Button(controls, text="Generate Report", command=self.generate_report_callback).grid(
            row=2, column=0, columnspan=4, pady=(6, 0), sticky="w"
        )

        table = ttk.LabelFrame(self.reports_tab, text="Report List")
        table.pack(fill="both", expand=True)
        self.report_list = ttk.Treeview(
            table,
            columns=("TransID", "Member", "Book", "BorrowDate", "DueDate", "ReturnDate", "Status", "Fine"),
            show="headings",
        )
        for col, width in [
            ("TransID", 90),
            ("Member", 160),
            ("Book", 220),
            ("BorrowDate", 120),
            ("DueDate", 120),
            ("ReturnDate", 120),
            ("Status", 100),
            ("Fine", 80),
        ]:
            self.report_list.heading(col, text=col)
            self.report_list.column(col, width=width, anchor="center")
        self.report_list.pack(fill="both", expand=True, pady=(0, 8))

        self.text_report = tk.Text(table, wrap="word", height=8)
        self.text_report.pack(fill="both", expand=True)

    def refresh_books(self, search_term=""):
        self.tree1.delete(*self.tree1.get_children())
        rows = search_books(search_term) if str(search_term).strip() else fetch_all_books()
        for row in rows:
            self.tree1.insert("", "end", values=row)

    def add_book_callback(self):
        try:
            title = self.title_entry.get().strip()
            author = self.author_entry.get().strip()
            year = parse_positive_int(self.year_entry.get().strip(), "Year")
            price = parse_positive_int(self.price_entry.get().strip(), "Price")
            available = parse_positive_int(self.available_entry.get().strip(), "Available", allow_zero=True)

            if not title or not author:
                raise ValueError("Title and author are required.")
            if year < 1500 or year >= 2100:
                raise ValueError("Year must be between 1500 and 2099.")

            insert_book(title, author, year, price, available)
            self.refresh_books()
            clear_entries([self.title_entry, self.author_entry, self.year_entry, self.price_entry, self.available_entry])
            messagebox.showinfo("Success", "Book added successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def update_book_callback(self):
        try:
            row = selected_row(self.tree1)
            title = self.title_entry.get().strip()
            author = self.author_entry.get().strip()
            year = parse_positive_int(self.year_entry.get().strip(), "Year")
            price = parse_positive_int(self.price_entry.get().strip(), "Price")
            available = parse_positive_int(self.available_entry.get().strip(), "Available", allow_zero=True)
            if not title or not author:
                raise ValueError("Title and author are required.")
            update_book(row[0], title, author, year, price, available)
            self.refresh_books()
            messagebox.showinfo("Success", "Book updated successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def delete_book_callback(self):
        try:
            row = selected_row(self.tree1)
            delete_book(row[0])
            self.refresh_books()
            clear_entries([self.title_entry, self.author_entry, self.year_entry, self.price_entry, self.available_entry])
            messagebox.showinfo("Success", "Book deleted successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def refresh_members(self):
        self.tree2.delete(*self.tree2.get_children())
        for row in fetch_all_members():
            self.tree2.insert("", "end", values=row)

    def add_member_callback(self):
        try:
            name = self.name_entry.get().strip()
            email = self.email_entry.get().strip()
            address = self.add_entry.get().strip()
            phone = self.ph_entry.get().strip()
            if not all([name, email, address, phone]):
                raise ValueError("All member fields are required.")
            insert_member(name, email, address, phone)
            self.refresh_members()
            clear_entries([self.name_entry, self.email_entry, self.add_entry, self.ph_entry])
            messagebox.showinfo("Success", "Member added successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def update_member_callback(self):
        try:
            row = selected_row(self.tree2)
            name = self.name_entry.get().strip()
            email = self.email_entry.get().strip()
            address = self.add_entry.get().strip()
            phone = self.ph_entry.get().strip()
            if not all([name, email, address, phone]):
                raise ValueError("All member fields are required.")
            update_member(row[0], name, email, address, phone)
            self.refresh_members()
            messagebox.showinfo("Success", "Member updated successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def delete_member_callback(self):
        try:
            row = selected_row(self.tree2)
            delete_member(row[0])
            self.refresh_members()
            clear_entries([self.name_entry, self.email_entry, self.add_entry, self.ph_entry])
            messagebox.showinfo("Success", "Member deleted successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def refresh_transactions(self):
        self.tree3.delete(*self.tree3.get_children())
        for row in fetch_transactions(self.status_var.get()):
            self.tree3.insert("", "end", values=row)

    def borrow_book_callback(self):
        try:
            member_id = resolve_member_id(self.memID_entry.get(), self.mem_entry.get())
            book_id = resolve_book_id(self.bookID_entry.get(), self.bookT_entry.get())
            days_to_return = parse_positive_int(self.returnDay_entry.get().strip(), "Days to return")
            create_borrow_transaction(member_id, book_id, days_to_return)
            self.refresh_transactions()
            self.refresh_books()
            clear_entries([self.mem_entry, self.memID_entry, self.bookT_entry, self.bookID_entry, self.returnDay_entry])
            messagebox.showinfo("Success", "Book issued successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def return_book_callback(self):
        try:
            row = selected_row(self.tree3)
            complete_return_transaction(row[0])
            self.refresh_transactions()
            self.refresh_books()
            messagebox.showinfo("Success", "Book returned successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def generate_report_callback(self):
        try:
            date_from = parse_date(self.entry_r_datefrom.get(), "Date From")
            date_to = parse_date(self.entry_r_dateto.get(), "Date To")
            member_name = self.entry_r_membername.get().strip()
            book_title = self.entry_r_booktitle.get().strip()
            records = filter_reports(date_from, date_to, member_name, book_title)

            self.report_list.delete(*self.report_list.get_children())
            for row in records:
                self.report_list.insert("", "end", values=row)

            self.text_report.delete("1.0", tk.END)
            self.text_report.insert(tk.END, build_report_text(records))
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


def run_app():
    root = tk.Tk()
    LibraryApp(root)
    root.mainloop()
