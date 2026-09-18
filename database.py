"""
database.py
Handles the MySQL connection and all CRUD / auth operations for the
Employee Management System.
"""

import hashlib
import mysql.connector
from mysql.connector import Error

# ---------------------------------------------------------------------------
# Update these to match your local MySQL setup, or set them as environment
# variables (recommended so you never commit real credentials to GitHub).
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "employee_management_system",
}


def get_connection():
    """Create and return a new MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise ConnectionError(f"Could not connect to MySQL: {e}")


def hash_password(password: str) -> str:
    """Return a SHA-256 hash of the given password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def verify_login(username: str, password: str) -> bool:
    """Check a username/password pair against the users table."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE username = %s", (username,)
        )
        row = cursor.fetchone()
        if row is None:
            return False
        return row[0] == hash_password(password)
    finally:
        cursor.close()
        conn.close()


def create_user(username: str, password: str, role: str = "admin") -> None:
    """Create a new login user (e.g. for a signup/admin-creation screen)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, hash_password(password), role),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------
def get_departments():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Employee CRUD
# ---------------------------------------------------------------------------
def add_employee(first_name, last_name, email, phone, department_id,
                  designation, salary, date_joined):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO employees
               (first_name, last_name, email, phone, department_id,
                designation, salary, date_joined)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (first_name, last_name, email, phone, department_id,
             designation, salary, date_joined),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_employee(employee_id, first_name, last_name, email, phone,
                     department_id, designation, salary, date_joined):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE employees
               SET first_name=%s, last_name=%s, email=%s, phone=%s,
                   department_id=%s, designation=%s, salary=%s, date_joined=%s
               WHERE employee_id=%s""",
            (first_name, last_name, email, phone, department_id,
             designation, salary, date_joined, employee_id),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def delete_employee(employee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE employee_id=%s", (employee_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def get_all_employees():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT e.employee_id, e.first_name, e.last_name, e.email, e.phone,
                      d.department_name, e.designation, e.salary, e.date_joined
               FROM employees e
               LEFT JOIN departments d ON e.department_id = d.department_id
               ORDER BY e.employee_id"""
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def search_employees(keyword):
    """Search by name, department, designation, or email."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        like = f"%{keyword}%"
        cursor.execute(
            """SELECT e.employee_id, e.first_name, e.last_name, e.email, e.phone,
                      d.department_name, e.designation, e.salary, e.date_joined
               FROM employees e
               LEFT JOIN departments d ON e.department_id = d.department_id
               WHERE e.first_name LIKE %s OR e.last_name LIKE %s
                  OR d.department_name LIKE %s OR e.designation LIKE %s
                  OR e.email LIKE %s
               ORDER BY e.employee_id""",
            (like, like, like, like, like),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_employee_by_id(employee_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM employees WHERE employee_id=%s", (employee_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
