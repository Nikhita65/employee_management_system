"""
app.py
Employee Management System — Tkinter desktop app backed by MySQL.

Features:
  - Login screen (authenticates against the `users` table)
  - Add / Update / Delete employees
  - Search employees by name, department, designation, or email
  - View salary and department records
  - Full CRUD against MySQL via database.py

Run:
    python app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database as db


# ===========================================================================
# LOGIN WINDOW
# ===========================================================================
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Employee Management System — Login")
        self.geometry("380x260")
        self.resizable(False, False)
        self.configure(bg="#f2f4f7")
        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self, bg="#f2f4f7")
        frame.pack(expand=True)

        tk.Label(frame, text="Employee Management System", font=("Segoe UI", 14, "bold"),
                 bg="#f2f4f7").grid(row=0, column=0, columnspan=2, pady=(10, 20))

        tk.Label(frame, text="Username", bg="#f2f4f7").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.username_entry = ttk.Entry(frame, width=25)
        self.username_entry.grid(row=1, column=1, padx=5, pady=8)

        tk.Label(frame, text="Password", bg="#f2f4f7").grid(row=2, column=0, sticky="e", padx=5, pady=8)
        self.password_entry = ttk.Entry(frame, width=25, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=8)

        ttk.Button(frame, text="Login", command=self._login).grid(
            row=3, column=0, columnspan=2, pady=20, ipadx=10)

        tk.Label(frame, text="Default: admin / admin123", fg="#888", bg="#f2f4f7",
                 font=("Segoe UI", 8)).grid(row=4, column=0, columnspan=2)

        self.bind("<Return>", lambda event: self._login())

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing info", "Please enter both username and password.")
            return

        try:
            if db.verify_login(username, password):
                self.destroy()
                MainApp().mainloop()
            else:
                messagebox.showerror("Login failed", "Invalid username or password.")
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))


# ===========================================================================
# MAIN APPLICATION WINDOW
# ===========================================================================
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Employee Management System")
        self.geometry("950x550")
        self.department_map = {}   # name -> id, for the dropdown
        self._build_ui()
        self._load_departments()
        self.refresh_table()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # --- Top: search bar ---
        top_frame = tk.Frame(self, pady=8)
        top_frame.pack(fill="x", padx=10)

        tk.Label(top_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<Return>", lambda e: self.search())

        ttk.Button(top_frame, text="Search", command=self.search).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Show All", command=self.refresh_table).pack(side="left", padx=5)

        # --- Middle: employee table ---
        columns = ("id", "first_name", "last_name", "email", "phone",
                   "department", "designation", "salary", "date_joined")
        headings = ("ID", "First Name", "Last Name", "Email", "Phone",
                    "Department", "Designation", "Salary", "Date Joined")

        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

        # --- Bottom: form + buttons ---
        form_frame = tk.LabelFrame(self, text="Employee Details", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        self.entries = {}
        fields = [("first_name", "First Name"), ("last_name", "Last Name"),
                  ("email", "Email"), ("phone", "Phone"),
                  ("designation", "Designation"), ("salary", "Salary"),
                  ("date_joined", "Date Joined (YYYY-MM-DD)")]

        for i, (key, label) in enumerate(fields):
            row, col = divmod(i, 4)
            tk.Label(form_frame, text=label).grid(row=row * 2, column=col, sticky="w", padx=5)
            entry = ttk.Entry(form_frame, width=20)
            entry.grid(row=row * 2 + 1, column=col, padx=5, pady=3)
            self.entries[key] = entry

        # Department dropdown
        dept_row, dept_col = divmod(len(fields), 4)
        tk.Label(form_frame, text="Department").grid(row=dept_row * 2, column=dept_col, sticky="w", padx=5)
        self.department_cb = ttk.Combobox(form_frame, width=18, state="readonly")
        self.department_cb.grid(row=dept_row * 2 + 1, column=dept_col, padx=5, pady=3)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Add Employee", command=self.add_employee).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_employee).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_employee).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=5)

        self.selected_id = None

    # ------------------------------------------------------------- helpers
    def _load_departments(self):
        try:
            departments = db.get_departments()
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))
            departments = []
        self.department_map = {name: dept_id for dept_id, name in departments}
        self.department_cb["values"] = list(self.department_map.keys())

    def _on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]
        self.entries["first_name"].delete(0, tk.END); self.entries["first_name"].insert(0, values[1])
        self.entries["last_name"].delete(0, tk.END); self.entries["last_name"].insert(0, values[2])
        self.entries["email"].delete(0, tk.END); self.entries["email"].insert(0, values[3])
        self.entries["phone"].delete(0, tk.END); self.entries["phone"].insert(0, values[4])
        self.department_cb.set(values[5] or "")
        self.entries["designation"].delete(0, tk.END); self.entries["designation"].insert(0, values[6])
        self.entries["salary"].delete(0, tk.END); self.entries["salary"].insert(0, values[7])
        self.entries["date_joined"].delete(0, tk.END); self.entries["date_joined"].insert(0, values[8] or "")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.department_cb.set("")
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

    def _get_form_data(self):
        dept_name = self.department_cb.get()
        department_id = self.department_map.get(dept_name)
        salary_text = self.entries["salary"].get().strip()
        try:
            salary = float(salary_text) if salary_text else 0.0
        except ValueError:
            raise ValueError("Salary must be a number.")

        return {
            "first_name": self.entries["first_name"].get().strip(),
            "last_name": self.entries["last_name"].get().strip(),
            "email": self.entries["email"].get().strip() or None,
            "phone": self.entries["phone"].get().strip() or None,
            "department_id": department_id,
            "designation": self.entries["designation"].get().strip() or None,
            "salary": salary,
            "date_joined": self.entries["date_joined"].get().strip() or None,
        }

    def _populate_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    # ------------------------------------------------------------- actions
    def refresh_table(self):
        try:
            rows = db.get_all_employees()
            self._populate_tree(rows)
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))

    def search(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh_table()
            return
        try:
            rows = db.search_employees(keyword)
            self._populate_tree(rows)
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))

    def add_employee(self):
        try:
            data = self._get_form_data()
        except ValueError as e:
            messagebox.showwarning("Invalid input", str(e))
            return

        if not data["first_name"] or not data["last_name"]:
            messagebox.showwarning("Missing info", "First and last name are required.")
            return

        try:
            db.add_employee(**data)
            messagebox.showinfo("Success", "Employee added.")
            self.clear_form()
            self.refresh_table()
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))

    def update_employee(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select an employee from the table first.")
            return
        try:
            data = self._get_form_data()
        except ValueError as e:
            messagebox.showwarning("Invalid input", str(e))
            return

        try:
            db.update_employee(self.selected_id, **data)
            messagebox.showinfo("Success", "Employee updated.")
            self.clear_form()
            self.refresh_table()
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))

    def delete_employee(self):
        if not self.selected_id:
            messagebox.showwarning("No selection", "Select an employee from the table first.")
            return
        if not messagebox.askyesno("Confirm delete", "Delete this employee record?"):
            return
        try:
            db.delete_employee(self.selected_id)
            messagebox.showinfo("Success", "Employee deleted.")
            self.clear_form()
            self.refresh_table()
        except ConnectionError as e:
            messagebox.showerror("Database error", str(e))


if __name__ == "__main__":
    LoginWindow().mainloop()
