# College Attendance Management System

This repository contains two implementations of the College Attendance Management System:

1. `flask_app/` — a Flask + SQLite + Bootstrap attendance web application.
2. `mysql_project/college_attendance.sql` — a database-focused MySQL mini project.
3. `docs/OPR_College_Attendance_Management_System.pdf` — the one-page OPR document.

**Important:** The Flask/SQLite application and the MySQL script are separate implementations with different schemas. Run and evaluate them separately; do not expect the MySQL tables to be used by the Flask app.

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

Open http://127.0.0.1:5000. On first launch, SQLite creates `attendance.db` automatically.

Initial demo login: `admin` / `admin123`. These are demo credentials only. Before deployment, set `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and a strong random `FLASK_SECRET_KEY` environment variable. Do not deploy using the demo credentials or development secret.

Features include admin login, student and subject create/read/update/delete operations, per-day attendance marking, attendance summary reports, a below-75% attendance list, database views, and an attendance-change audit trigger.

## MySQL database project

Open `mysql_project/college_attendance.sql` in MySQL Workbench and execute it from top to bottom. The script creates and seeds the schema and demonstrates CRUD operations, inner/left joins, aggregate queries, attendance percentages, a summary view, a trigger blocking future attendance, and transaction commit/rollback examples. The sample transaction uses an upsert so its demonstration records can be applied repeatedly.

### Quick verification after running the SQL script

Run these queries in MySQL Workbench:

```sql
USE college_attendance;
SHOW TABLES;
SELECT * FROM students;
SELECT * FROM subjects;
SELECT * FROM attendance;
SELECT * FROM student_attendance_summary;
```

Expected: the schema tables are listed, sample students/subjects/attendance rows are visible, and the summary view returns attendance totals and percentages. The SQL file should be executed in a MySQL-compatible database; a phone browser or GitHub app alone does not execute it.

## Before submission

- Run the MySQL script in MySQL Workbench and resolve any error messages.
- Run the Flask application and test student/subject forms, attendance marking, and reports.
- Capture screenshots from actual successful runs; do not use mock screenshots as execution proof.
- Prepare the detailed DBMS report and submit the source, SQL script, and report through the required classroom portal.

## Owner

Swapnil Patil — https://github.com/SwapnilPatil-1993/College-Attendance-Management-System
