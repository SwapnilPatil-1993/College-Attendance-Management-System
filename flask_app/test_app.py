"""Basic automated tests for the Flask + SQLite attendance app.

Run from this directory with:
    python -m unittest test_app.py

The tests use a temporary SQLite database and do not change attendance.db.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

TEST_DIR = tempfile.TemporaryDirectory()
os.environ["ATTENDANCE_DB"] = str(Path(TEST_DIR.name) / "test_attendance.db")
os.environ["FLASK_SECRET_KEY"] = "test-only-secret-key"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "admin123"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import app as attendance_app  # noqa: E402


class AttendanceAppTests(unittest.TestCase):
    def setUp(self):
        db_path = Path(os.environ["ATTENDANCE_DB"])
        if db_path.exists():
            db_path.unlink()
        attendance_app.app.config.update(TESTING=True)
        attendance_app.init_db()
        self.client = attendance_app.app.test_client()

    def login(self):
        return self.client.post(
            "/login", data={"username": "admin", "password": "admin123"},
            follow_redirects=True,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_login_and_dashboard_load(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard", response.data)

    def test_student_can_be_created_and_listed(self):
        self.login()
        response = self.client.post("/students", data={
            "roll_no": "TEST001", "name": "Test Student",
            "email": "test.student@example.com", "new_department": "IT", "year": "3",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Student", response.data)

    def test_reports_page_loads(self):
        self.login()
        response = self.client.get("/reports")
        self.assertEqual(response.status_code, 200)

    def test_invalid_login_does_not_authenticate(self):
        response = self.client.post("/login", data={
            "username": "wrong", "password": "wrong",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        dashboard = self.client.get("/")
        self.assertEqual(dashboard.status_code, 302)


if __name__ == "__main__":
    unittest.main()
