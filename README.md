# Employee Management System

A desktop Employee Management System built with **Python (Tkinter)** for the GUI and **MySQL** for data storage. Built as a portfolio/practice project demonstrating core CRUD operations, authentication, and relational database design.

## Features

- 🔐 **Login system** — authenticates against a `users` table (passwords stored as SHA-256 hashes, not plain text)
- ➕ **Add employees** — name, email, phone, department, designation, salary, date joined
- ✏️ **Update employees** — edit any field for an existing record
- ❌ **Delete employees** — remove a record with a confirmation prompt
- 🔍 **Search employees** — search by name, department, designation, or email
- 💰 **Salary & department records** — department is a foreign key to a `departments` table; salary is stored as `DECIMAL(10,2)` for accuracy
- 🗄️ **Full CRUD against MySQL** — all operations go through parameterized queries (no SQL injection risk)

## Tech Stack

| Layer      | Technology              |
|------------|--------------------------|
| GUI        | Python 3, Tkinter (built-in) |
| Database   | MySQL 8.x                |
| DB Driver  | `mysql-connector-python` |
| Auth       | SHA-256 password hashing |

## Project Structure

```
employee-management-system/
├── app.py           # Tkinter GUI (login window + main CRUD window)
├── database.py       # MySQL connection + all CRUD/auth functions
├── schema.sql         # Database schema, tables, seed data
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/employee-management-system.git
cd employee-management-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up the database
Open MySQL and run:
```bash
mysql -u root -p < schema.sql
```
This creates the `employee_management_system` database, the `users`, `departments`, and `employees` tables, a few seed departments, and a default login (**username: `admin`**, **password: `admin123`**).

### 4. Configure your connection
Edit the `DB_CONFIG` dictionary at the top of `database.py` with your MySQL host/user/password:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "employee_management_system",
}
```
> For a real deployment, load these from environment variables instead of hardcoding them.

### 5. Run the app
```bash
python app.py
```

## Database Schema

**users** — `user_id`, `username`, `password` (hashed), `role`, `created_at`
**departments** — `department_id`, `department_name`
**employees** — `employee_id`, `first_name`, `last_name`, `email`, `phone`, `department_id` (FK → departments), `designation`, `salary`, `date_joined`, `created_at`, `updated_at`

## Possible Future Enhancements

- Password reset / multiple user roles (admin vs. viewer)
- Export employee list to CSV/PDF
- Attendance and leave tracking module
- Pagination for large employee lists
- Migrate GUI to a web app (Flask/Django) for browser access

## License

This project is open source and available under the [MIT License](LICENSE).
