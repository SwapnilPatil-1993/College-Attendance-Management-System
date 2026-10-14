import os
import sqlite3
from contextlib import closing
from datetime import date
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("ATTENDANCE_DB", BASE_DIR / "attendance.db"))
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "development-only-change-me")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with closing(sqlite3.connect(DATABASE)) as db:
        db.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            dept_id INTEGER NOT NULL REFERENCES departments(dept_id),
            year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 4)
        );
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            dept_id INTEGER NOT NULL REFERENCES departments(dept_id),
            year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 4),
            UNIQUE(subject_name, dept_id, year)
        );
        CREATE TABLE IF NOT EXISTS attendance (
            att_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
            att_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
            UNIQUE(student_id, subject_id, att_date)
        );
        CREATE TABLE IF NOT EXISTS attendance_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            att_id INTEGER NOT NULL,
            old_status TEXT NOT NULL,
            new_status TEXT NOT NULL,
            changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TRIGGER IF NOT EXISTS log_attendance_change
        AFTER UPDATE OF status ON attendance
        WHEN OLD.status <> NEW.status
        BEGIN
            INSERT INTO attendance_log(att_id, old_status, new_status)
            VALUES (OLD.att_id, OLD.status, NEW.status);
        END;
        CREATE VIEW IF NOT EXISTS attendance_summary AS
        SELECT s.student_id, s.roll_no, s.name, sub.subject_id, sub.subject_name,
               COUNT(a.att_id) AS total_classes,
               COALESCE(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END),0) AS present_count,
               ROUND(100.0 * COALESCE(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END),0)
                     / NULLIF(COUNT(a.att_id),0), 2) AS attendance_percentage
        FROM students s CROSS JOIN subjects sub
        LEFT JOIN attendance a ON a.student_id=s.student_id AND a.subject_id=sub.subject_id
        GROUP BY s.student_id, sub.subject_id;
        CREATE VIEW IF NOT EXISTS low_attendance_view AS
        SELECT * FROM attendance_summary
        WHERE total_classes > 0 AND attendance_percentage < 75;
        """)
        db.commit()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD", "admin123")
        if request.form.get("username") == username and request.form.get("password") == password:
            session["admin"] = True
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
@login_required
def dashboard():
    db = get_db()
    counts = {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
              for table in ("students", "subjects", "attendance")}
    low = db.execute("SELECT COUNT(DISTINCT student_id) FROM low_attendance_view").fetchone()[0]
    return render_template("dashboard.html", counts=counts, low=low)


@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    db = get_db()
    departments = db.execute("SELECT * FROM departments ORDER BY dept_name").fetchall()
    if request.method == "POST":
        try:
            dept_name = request.form.get("new_department", "").strip()
            dept_id = request.form.get("dept_id")
            if dept_name:
                db.execute("INSERT OR IGNORE INTO departments(dept_name) VALUES (?)", (dept_name,))
                dept_id = db.execute("SELECT dept_id FROM departments WHERE dept_name=?", (dept_name,)).fetchone()[0]
            db.execute("INSERT INTO students(roll_no,name,email,dept_id,year) VALUES(?,?,?,?,?)",
                       (request.form["roll_no"].strip(), request.form["name"].strip(),
                        request.form["email"].strip(), int(dept_id), int(request.form["year"])))
            db.commit()
            flash("Student added.", "success")
        except (sqlite3.IntegrityError, ValueError, KeyError, TypeError) as exc:
            db.rollback()
            flash(f"Could not add student: {exc}", "danger")
        return redirect(url_for("students"))
    rows = db.execute("SELECT s.*, d.dept_name FROM students s JOIN departments d USING(dept_id) ORDER BY s.roll_no").fetchall()
    return render_template("students.html", students=rows, departments=departments)


@app.post("/students/<int:student_id>/delete")
@login_required
def delete_student(student_id):
    db = get_db()
    db.execute("DELETE FROM students WHERE student_id=?", (student_id,))
    db.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("students"))


@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    db = get_db()
    student = db.execute("SELECT * FROM students WHERE student_id=?", (student_id,)).fetchone()
    if student is None:
        abort(404)
    departments = db.execute("SELECT * FROM departments ORDER BY dept_name").fetchall()
    if request.method == "POST":
        try:
            db.execute("UPDATE students SET roll_no=?,name=?,email=?,dept_id=?,year=? WHERE student_id=?",
                       (request.form["roll_no"].strip(), request.form["name"].strip(),
                        request.form["email"].strip(), int(request.form["dept_id"]),
                        int(request.form["year"]), student_id))
            db.commit()
            flash("Student updated.", "success")
            return redirect(url_for("students"))
        except (sqlite3.IntegrityError, ValueError) as exc:
            db.rollback()
            flash(f"Could not update student: {exc}", "danger")
    return render_template("edit_student.html", student=student, departments=departments)


@app.route("/subjects", methods=["GET", "POST"])
@login_required
def subjects():
    db = get_db()
    if request.method == "POST":
        try:
            dept_name = request.form.get("new_department", "").strip()
            dept_id = request.form.get("dept_id")
            if dept_name:
                db.execute("INSERT OR IGNORE INTO departments(dept_name) VALUES (?)", (dept_name,))
                dept_id = db.execute("SELECT dept_id FROM departments WHERE dept_name=?", (dept_name,)).fetchone()[0]
            db.execute("INSERT INTO subjects(subject_name,dept_id,year) VALUES(?,?,?)",
                       (request.form["subject_name"].strip(), int(dept_id), int(request.form["year"])))
            db.commit()
            flash("Subject added.", "success")
        except (sqlite3.IntegrityError, ValueError, KeyError, TypeError) as exc:
            db.rollback()
            flash(f"Could not add subject: {exc}", "danger")
        return redirect(url_for("subjects"))
    rows = db.execute("SELECT sub.*, d.dept_name FROM subjects sub JOIN departments d USING(dept_id) ORDER BY sub.subject_name").fetchall()
    departments = db.execute("SELECT * FROM departments ORDER BY dept_name").fetchall()
    return render_template("subjects.html", subjects=rows, departments=departments)


@app.post("/subjects/<int:subject_id>/delete")
@login_required
def delete_subject(subject_id):
    db = get_db()
    db.execute("DELETE FROM subjects WHERE subject_id=?", (subject_id,))
    db.commit()
    flash("Subject deleted.", "success")
    return redirect(url_for("subjects"))


@app.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
def edit_subject(subject_id):
    db = get_db()
    subject = db.execute("SELECT * FROM subjects WHERE subject_id=?", (subject_id,)).fetchone()
    if subject is None:
        abort(404)
    departments = db.execute("SELECT * FROM departments ORDER BY dept_name").fetchall()
    if request.method == "POST":
        try:
            db.execute("UPDATE subjects SET subject_name=?,dept_id=?,year=? WHERE subject_id=?",
                       (request.form["subject_name"].strip(), int(request.form["dept_id"]),
                        int(request.form["year"]), subject_id))
            db.commit()
            flash("Subject updated.", "success")
            return redirect(url_for("subjects"))
        except (sqlite3.IntegrityError, ValueError) as exc:
            db.rollback()
            flash(f"Could not update subject: {exc}", "danger")
    return render_template("edit_subject.html", subject=subject, departments=departments)


@app.route("/attendance", methods=["GET", "POST"])
@login_required
def mark_attendance():
    db = get_db()
    if request.method == "POST":
        subject_id, att_date = int(request.form["subject_id"]), request.form["att_date"]
        if att_date > date.today().isoformat():
            flash("Attendance cannot be marked for a future date.", "danger")
        else:
            try:
                with db:
                    for student in db.execute("SELECT student_id FROM students").fetchall():
                        status = "Present" if str(student["student_id"]) in request.form.getlist("present") else "Absent"
                        db.execute("INSERT INTO attendance(student_id,subject_id,att_date,status) VALUES(?,?,?,?) "
                                   "ON CONFLICT(student_id,subject_id,att_date) DO UPDATE SET status=excluded.status",
                                   (student["student_id"], subject_id, att_date, status))
                flash("Attendance saved.", "success")
            except sqlite3.Error as exc:
                flash(f"Attendance was not saved: {exc}", "danger")
        return redirect(url_for("mark_attendance", subject_id=subject_id, att_date=att_date))
    subject_id = request.args.get("subject_id", type=int)
    att_date = request.args.get("att_date", date.today().isoformat())
    subjects_list = db.execute("SELECT * FROM subjects ORDER BY subject_name").fetchall()
    students_list = []
    if subject_id:
        students_list = db.execute("""SELECT s.*, a.status FROM students s
            LEFT JOIN attendance a ON a.student_id=s.student_id AND a.subject_id=? AND a.att_date=?
            ORDER BY s.roll_no""", (subject_id, att_date)).fetchall()
    return render_template("attendance.html", subjects=subjects_list, students=students_list,
                           subject_id=subject_id, att_date=att_date, today=date.today().isoformat())


@app.get("/reports")
@login_required
def reports():
    db = get_db()
    summary = db.execute("SELECT * FROM attendance_summary WHERE total_classes>0 ORDER BY name,subject_name").fetchall()
    low = db.execute("SELECT * FROM low_attendance_view ORDER BY attendance_percentage, name").fetchall()
    return render_template("reports.html", summary=summary, low=low)


# Initialize the schema for both direct execution and production WSGI servers (e.g. Gunicorn).
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get("FLASK_DEBUG") == "1")
