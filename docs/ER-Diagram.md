# ER Diagram — College Attendance Management System

This ER diagram matches the **Flask + SQLite** schema in `flask_app/app.py`.

```mermaid
erDiagram
    DEPARTMENTS ||--o{ STUDENTS : has
    DEPARTMENTS ||--o{ SUBJECTS : offers
    STUDENTS ||--o{ ATTENDANCE : receives
    SUBJECTS ||--o{ ATTENDANCE : records
    ATTENDANCE ||--o{ ATTENDANCE_LOG : changes_logged

    DEPARTMENTS {
        int dept_id PK
        string dept_name UK
    }
    STUDENTS {
        int student_id PK
        string roll_no UK
        string name
        string email UK
        int dept_id FK
        int year
    }
    SUBJECTS {
        int subject_id PK
        string subject_name
        int dept_id FK
        int year
    }
    ATTENDANCE {
        int att_id PK
        int student_id FK
        int subject_id FK
        string att_date
        string status
    }
    ATTENDANCE_LOG {
        int log_id PK
        int att_id
        string old_status
        string new_status
        datetime changed_at
    }
```

## Relationship notes
- One department can have many students and many subjects.
- One student can have many attendance records; each record belongs to one student and one subject.
- One subject can have many attendance records.
- The `log_attendance_change` trigger records status changes in `attendance_log`.
- `attendance_summary` and `low_attendance_view` are database views, not base entities.

**Schema note:** This diagram represents the Flask/SQLite application. The separate MySQL mini-project schema has different columns and includes a `faculty` table; do not treat the two schemas as identical.
