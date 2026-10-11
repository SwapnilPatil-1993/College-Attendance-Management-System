# College Attendance Management System

This repository contains the two deliverables described in the supplied project documents:

1. `flask_app/` implements the one-page OPR: a Flask, SQLite, Bootstrap attendance web application.
2. `mysql_project/college_attendance.sql` implements the database-only MySQL mini project from the detailed report.
3. `docs/OPR_College_Attendance_Management_System.pdf` is the revised one-page OPR with Swapnil Patil's project repository link.

## Flask + SQLite application

Requirements: Python 3.10+.

```powershell
cd flask_app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FLASK_SECRET_KEY = 'replace-this-with-a-random-secret'
python app.py
```

Open http://127.0.0.1:5000. Initial admin credentials: `admin` / `admin123` (change these before deployment with `ADMIN_USERNAME` and `ADMIN_PASSWORD`). SQLite creates `attendance.db` on first launch. Features include admin session login, student and subject CRUD, per-day attendance marking, joined attendance reports, and the under-75% list. Database views and an audit trigger are created automatically.

## MySQL project

Open `mysql_project/college_attendance.sql` in MySQL Workbench and run it top to bottom. It creates and seeds the database, creates the schema, demonstrates CRUD, joins, aggregates, the attendance view, a future-date trigger, and transaction commit/rollback examples.

The two supplied documents specify distinct technology stacks and scopes; they are preserved as two implementations instead of silently treating SQLite and MySQL as the same build.

## Owner

Swapnil Patil — https://github.com/SwapnilPatil-1993/College-Attendance-Management-System
