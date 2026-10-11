-- College Attendance Management System (MySQL / MySQL Workbench)
-- Run from top to bottom. Uses the schema and sample data in the detailed report.
CREATE DATABASE IF NOT EXISTS college_attendance;
USE college_attendance;

CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT PRIMARY KEY AUTO_INCREMENT,
    faculty_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE
);
CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_name VARCHAR(100) NOT NULL,
    roll_no VARCHAR(20) UNIQUE,
    gender ENUM('Male','Female','Other') NOT NULL,
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    department VARCHAR(100) NOT NULL,
    semester INT CHECK (semester BETWEEN 1 AND 8)
);
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT PRIMARY KEY AUTO_INCREMENT,
    subject_name VARCHAR(100) NOT NULL,
    faculty_id INT,
    semester INT CHECK (semester BETWEEN 1 AND 8),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present','Absent') NOT NULL DEFAULT 'Present',
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    UNIQUE (student_id, subject_id, attendance_date)
);

INSERT IGNORE INTO faculty (faculty_id,faculty_name,department,phone,email) VALUES
(1,'Rahul Sharma','Computer Science','9000000001','rahul.sharma@college.edu'),
(2,'Priya Patil','Computer Science','9000000002','priya.patil@college.edu'),
(3,'Amit Verma','E&TC','9000000003','amit.verma@college.edu');
INSERT IGNORE INTO students (student_id,student_name,roll_no,gender,phone,email,department,semester) VALUES
(1,'Aarav Joshi','CS101','Male','9100000001','aarav@college.edu','Computer Science',5),
(2,'Sneha Kulkarni','CS102','Female','9100000002','sneha@college.edu','Computer Science',5),
(3,'Rohan Patil','ET103','Male','9100000003','rohan@college.edu','E&TC',5),
(4,'Ananya Deshmukh','DS104','Female','9100000004','ananya@college.edu','Data Science',5),
(5,'Vivek Singh','CS105','Male','9100000005','vivek@college.edu','Computer Science',5);
INSERT IGNORE INTO subjects (subject_id,subject_name,faculty_id,semester) VALUES
(1,'DBMS',1,5),(2,'Computer Networks',2,5),(3,'Operating Systems',3,5);
INSERT IGNORE INTO attendance (attendance_id,student_id,subject_id,attendance_date,status) VALUES
(1,1,1,'2026-09-01','Present'),(2,2,1,'2026-09-01','Present'),
(3,3,2,'2026-09-01','Absent'),(4,4,1,'2026-09-02','Present'),
(5,5,2,'2026-09-02','Present');

-- CRUD demonstrations. Wrapped in a transaction so rerunning the script does not
-- permanently apply the example edits/deletion.
START TRANSACTION;
UPDATE students SET phone='9199999999' WHERE student_id=1;
UPDATE attendance SET status='Present' WHERE attendance_id=3;
DELETE FROM attendance WHERE attendance_id=5;
ROLLBACK;

-- Attendance detail join.
SELECT s.student_id,s.student_name,sub.subject_name,a.attendance_date,a.status
FROM students s
JOIN attendance a ON a.student_id=s.student_id
JOIN subjects sub ON sub.subject_id=a.subject_id;

-- Subject-wise present count.
SELECT sub.subject_name,COUNT(*) AS present_count
FROM attendance a JOIN subjects sub ON sub.subject_id=a.subject_id
WHERE a.status='Present' GROUP BY sub.subject_id,sub.subject_name;

-- Attendance percentage by student and by subject.
SELECT s.student_id,s.student_name,sub.subject_name,
       ROUND(100.0*SUM(a.status='Present')/NULLIF(COUNT(a.attendance_id),0),2) AS attendance_percentage
FROM students s JOIN attendance a ON a.student_id=s.student_id
JOIN subjects sub ON sub.subject_id=a.subject_id
GROUP BY s.student_id,s.student_name,sub.subject_id,sub.subject_name;

-- Present and absent counts per subject, including subjects with no records.
SELECT sub.subject_name,
       COALESCE(SUM(a.status='Present'),0) AS present_count,
       COALESCE(SUM(a.status='Absent'),0) AS absent_count
FROM subjects sub LEFT JOIN attendance a ON a.subject_id=sub.subject_id
GROUP BY sub.subject_id,sub.subject_name;

CREATE OR REPLACE VIEW student_attendance_summary AS
SELECT s.student_id,s.student_name,s.roll_no,sub.subject_id,sub.subject_name,
       COUNT(a.attendance_id) AS total_classes,
       COALESCE(SUM(a.status='Present'),0) AS classes_present,
       ROUND(100.0*COALESCE(SUM(a.status='Present'),0)/NULLIF(COUNT(a.attendance_id),0),2)
           AS attendance_percentage
FROM students s CROSS JOIN subjects sub
LEFT JOIN attendance a ON a.student_id=s.student_id AND a.subject_id=sub.subject_id
GROUP BY s.student_id,s.student_name,s.roll_no,sub.subject_id,sub.subject_name;
SELECT * FROM student_attendance_summary;
SELECT * FROM student_attendance_summary
WHERE total_classes>0 AND attendance_percentage<75;

DROP TRIGGER IF EXISTS trg_block_future_attendance;
DELIMITER //
CREATE TRIGGER trg_block_future_attendance
BEFORE INSERT ON attendance
FOR EACH ROW
BEGIN
    IF NEW.attendance_date > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT='Attendance cannot be marked for a future date';
    END IF;
END//
DELIMITER ;

-- Atomic example: commit all records for a day's attendance together.
START TRANSACTION;
INSERT INTO attendance(student_id,subject_id,attendance_date,status) VALUES
(1,2,'2026-09-03','Present'),(2,2,'2026-09-03','Absent'),(3,2,'2026-09-03','Present');
COMMIT;
-- Demonstrate undoing an accidental deletion.
START TRANSACTION;
DELETE FROM attendance WHERE attendance_date='2026-09-03';
ROLLBACK;
