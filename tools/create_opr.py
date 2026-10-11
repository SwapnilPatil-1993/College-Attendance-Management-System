from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


OUT = Path(__file__).resolve().parents[1] / "docs" / "OPR_College_Attendance_Management_System.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

navy = colors.HexColor("#14335B")
blue = colors.HexColor("#1F5D9B")
light = colors.HexColor("#EAF1F8")
gray = colors.HexColor("#4B5563")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17,
                          leading=20, textColor=navy, alignment=TA_CENTER, spaceAfter=2))
styles.add(ParagraphStyle(name="SubTitle", parent=styles["Normal"], fontSize=9, leading=12, textColor=gray,
                          alignment=TA_CENTER, spaceAfter=9))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=9.2,
                          leading=11, textColor=blue, spaceBefore=4, spaceAfter=2))
styles.add(ParagraphStyle(name="BodySmall", parent=styles["BodyText"], fontSize=8, leading=10.2,
                          textColor=colors.HexColor("#202833"), spaceAfter=1))
styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontSize=7.5, leading=9,
                          textColor=colors.HexColor("#202833")))
styles.add(ParagraphStyle(name="CellBold", parent=styles["Cell"], fontName="Helvetica-Bold", textColor=navy))
styles.add(ParagraphStyle(name="CellHeader", parent=styles["Cell"], fontName="Helvetica-Bold", textColor=colors.white))

P = lambda text, style="BodySmall": Paragraph(text, styles[style])
story = [P("COLLEGE ATTENDANCE MANAGEMENT SYSTEM", "TitleCustom"),
         P("DBMS MINI PROJECT - ONE PAGE REPORT", "SubTitle")]

meta = [
    [P("Project title", "CellBold"), P("College Attendance Management System", "Cell"),
     P("Database", "CellBold"), P("SQLite (sqlite3)", "Cell")],
    [P("Frontend", "CellBold"), P("HTML, Bootstrap, Jinja2", "Cell"),
     P("Backend", "CellBold"), P("Python 3, Flask", "Cell")],
    [P("Tools", "CellBold"), P("VS Code, GitHub", "Cell"),
     P("Project type", "CellBold"), P("Database-driven web application", "Cell")],
]
t = Table(meta, colWidths=[24*mm, 57*mm, 24*mm, 67*mm])
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), light), ("BOX",(0,0),(-1,-1),0.45,colors.HexColor("#C8D6E5")),
                       ("INNERGRID",(0,0),(-1,-1),0.35,colors.HexColor("#C8D6E5")),
                       ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),5),
                       ("RIGHTPADDING",(0,0),(-1,-1),5), ("TOPPADDING",(0,0),(-1,-1),4),
                       ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
story += [t, Spacer(1, 4)]

def section(title, text):
    story.extend([P(title, "Section"), P(text)])

section("INTRODUCTION AND PROBLEM STATEMENT", "The system stores students, subjects and daily attendance in a relational database. Staff can manage records, mark attendance, and quickly identify students whose attendance is below 75%.")
section("OBJECTIVE", "Build a backend and frontend supporting Create, Read, Update and Delete (CRUD). Apply SQL joins, views, a trigger and transactions, and generate attendance reports.")

story.append(P("DATABASE DESIGN", "Section"))
schema = [
    [P("Table", "CellHeader"), P("Columns and constraints", "CellHeader")],
    [P("Departments", "CellBold"), P("dept_id PK; dept_name UNIQUE", "Cell")],
    [P("Students", "CellBold"), P("student_id PK; roll_no and email UNIQUE; dept_id FK; year CHECK 1-4", "Cell")],
    [P("Subjects", "CellBold"), P("subject_id PK; dept_id FK; year CHECK 1-4", "Cell")],
    [P("Attendance", "CellBold"), P("att_id PK; student_id and subject_id FKs; UNIQUE(student, subject, date); status CHECK Present/Absent; cascade deletes", "Cell")],
    [P("Attendance log", "CellBold"), P("log_id PK; att_id, old_status, new_status, changed_at; populated by trigger", "Cell")],
]
t = Table(schema, colWidths=[38*mm, 134*mm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),navy), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                       ("BACKGROUND",(0,1),(0,-1),light), ("ROWBACKGROUNDS",(1,1),(-1,-1),[colors.white,colors.HexColor("#F7F9FC")]),
                       ("BOX",(0,0),(-1,-1),0.45,colors.HexColor("#C8D6E5")), ("INNERGRID",(0,0),(-1,-1),0.3,colors.HexColor("#D8E1EB")),
                       ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),5),
                       ("RIGHTPADDING",(0,0),(-1,-1),5), ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3)]))
story += [t, Spacer(1, 2)]

section("IMPLEMENTATION", "Backend (Flask): admin login with session, student and subject CRUD, attendance marking, dashboard counts, and reports. Frontend: Bootstrap pages for login, dashboard, students, subjects, attendance checkbox sheet, and reports. SQL features: attendance_summary and low_attendance_view (<75%), relational constraints, audit trigger, and transaction-based daily attendance.")
section("RELATIONSHIPS", "Departments 1:N students; departments 1:N subjects; students 1:N attendance; subjects 1:N attendance. Attendance connects students and subjects by date.")
section("CONCLUSION AND FUTURE SCOPE", "The project demonstrates normalization, constraints, joins, views and transaction management. Future extensions include teacher and student logins, charts, PDF export and automatic low-attendance alerts.")

story.append(Spacer(1, 3))
owner = Table([[P("BY: Swapnil Patil", "CellBold"),
                P('GitHub: <link href="https://github.com/SwapnilPatil-1993" color="#1F5D9B">https://github.com/SwapnilPatil-1993</link>', "Cell")]],
              colWidths=[61*mm, 111*mm])
owner.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),light), ("BOX",(0,0),(-1,-1),0.45,colors.HexColor("#C8D6E5")),
                           ("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),6),
                           ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5)]))
story.append(owner)

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=19*mm, leftMargin=19*mm,
                        topMargin=12*mm, bottomMargin=12*mm, title="College Attendance Management System - OPR",
                        author="Swapnil Patil")
doc.build(story)
print(OUT)
