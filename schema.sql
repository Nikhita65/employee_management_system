-- Employee Management System - Database Schema
-- Run this once in MySQL to create the database, tables, and a default admin user.

CREATE DATABASE IF NOT EXISTS employee_management_system;
USE employee_management_system;

-- Users table (for login/authentication)
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,   -- stored as a SHA-256 hash
    role        VARCHAR(20) NOT NULL DEFAULT 'admin',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id     INT AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    phone           VARCHAR(20),
    department_id   INT,
    designation     VARCHAR(100),
    salary          DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    date_joined     DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE SET NULL
);

-- Seed a few departments
INSERT INTO departments (department_name) VALUES
    ('Engineering'), ('Human Resources'), ('Sales'), ('Finance'), ('Support')
ON DUPLICATE KEY UPDATE department_name = department_name;

-- Default login: username "admin", password "admin123"
-- (password below is the SHA-256 hash of "admin123" — the app hashes passwords the same way)
INSERT INTO users (username, password, role) VALUES
    ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a', 'admin')
ON DUPLICATE KEY UPDATE username = username;
