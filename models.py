import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "scholarship_bridge.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT DEFAULT 'Admin'
        );

        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            university TEXT NOT NULL,
            country TEXT NOT NULL,
            degree_level TEXT NOT NULL,
            vacancies INTEGER DEFAULT 0,
            deadline TEXT NOT NULL,
            funding_type TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            benefits TEXT,
            requirements TEXT,
            image_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            country TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            avatar TEXT,
            degree_level TEXT,
            university_interest TEXT,
            field_of_study TEXT,
            phone TEXT,
            registered_on TEXT,
            last_login TEXT,
            total_applications INTEGER DEFAULT 0,
            saved_scholarships INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scholarship_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            applied_on TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scholarship_id) REFERENCES scholarships(id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            icon TEXT DEFAULT 'bell',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cur.execute("SELECT COUNT(*) FROM admin")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO admin (username, password, name) VALUES (?, ?, ?)",
            ("admin", "admin123", "Admin"),
        )

    cur.execute("SELECT COUNT(*) FROM scholarships")
    if cur.fetchone()[0] == 0:
        seed_scholarships(cur)

    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        seed_students(cur)

    cur.execute("SELECT COUNT(*) FROM applications")
    if cur.fetchone()[0] == 0:
        seed_applications(cur)

    cur.execute("SELECT COUNT(*) FROM notifications")
    if cur.fetchone()[0] == 0:
        seed_notifications(cur)

    conn.commit()
    conn.close()


def seed_scholarships(cur):
    scholarships = [
        (
            "DAAD Scholarship Program 2025",
            "Technical University of Munich",
            "Germany",
            "Master's",
            45,
            "2025-12-31",
            "Fully Funded",
            "Open",
            "The DAAD Scholarship Program offers fully funded opportunities for international students pursuing master's degrees in Germany.",
            "Full tuition coverage|Monthly stipend of €934|Health insurance|Travel allowance",
            "Bachelor's degree with strong academic record|English or German proficiency|Research proposal for selected programs",
            "https://images.unsplash.com/photo-1562774053-701939374585?w=800&q=80",
        ),
        (
            "Chevening Scholarship",
            "University of Oxford",
            "United Kingdom",
            "Master's",
            30,
            "2025-11-15",
            "Fully Funded",
            "Closing Soon",
            "Chevening Scholarships are the UK government's global scholarship programme, funded by the Foreign, Commonwealth & Development Office.",
            "Full tuition fees|Monthly living allowance|Return airfare|Additional grants",
            "Minimum 2 years work experience|Undergraduate degree|Leadership potential",
            "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800&q=80",
        ),
        (
            "MEXT Research Scholarship",
            "University of Tokyo",
            "Japan",
            "PhD",
            20,
            "2025-10-01",
            "Fully Funded",
            "Open",
            "MEXT scholarships support international students for graduate-level research in Japan.",
            "Full tuition|Monthly stipend ¥143,000|Round-trip airfare",
            "Research proposal|Supervisor acceptance|Language proficiency",
            "https://images.unsplash.com/photo-1540959733336-eab4deabeeaf?w=800&q=80",
        ),
        (
            "Erasmus Mundus Joint Masters",
            "Multiple European Universities",
            "Europe",
            "Master's",
            50,
            "2025-01-10",
            "Fully Funded",
            "Closed",
            "Erasmus Mundus Joint Master Degrees are prestigious, integrated, international study programmes.",
            "Full tuition waiver|Travel costs|Installation costs|Monthly allowance",
            "Bachelor's degree|English proficiency|Motivation letter",
            "https://images.unsplash.com/photo-1498243691581-b145c3f44a4a?w=800&q=80",
        ),
        (
            "Fulbright Foreign Student Program",
            "Harvard University",
            "USA",
            "Master's",
            25,
            "2025-09-30",
            "Fully Funded",
            "Open",
            "The Fulbright Program offers grants to study, teach and conduct research for international students in the United States.",
            "Tuition and fees|Living stipend|Health insurance|Book allowance",
            "Bachelor's degree|English proficiency|Leadership qualities",
            "https://images.unsplash.com/photo-1607237138185-eedd9c632b59?w=800&q=80",
        ),
    ]
    cur.executemany(
        """INSERT INTO scholarships
        (title, university, country, degree_level, vacancies, deadline,
         funding_type, status, description, benefits, requirements, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        scholarships,
    )


def seed_students(cur):
    now = datetime.now()
    students = [
        ("Ayesha Khan", "ayesha.khan@email.com", "Pakistan", "Active", "AK", "Master's", "Oxford University", "Computer Science", "+92 300 1234567", (now - timedelta(days=120)).strftime("%Y-%m-%d"), (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"), 3, 5),
        ("James Wilson", "james.w@email.com", "USA", "Active", "JW", "PhD", "MIT", "Engineering", "+1 555 0123", (now - timedelta(days=90)).strftime("%Y-%m-%d"), (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), 2, 8),
        ("Maria Santos", "maria.s@email.com", "Brazil", "Active", "MS", "Master's", "TU Munich", "Business", "+55 11 98765", (now - timedelta(days=60)).strftime("%Y-%m-%d"), (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"), 1, 3),
        ("Ahmed Hassan", "ahmed.h@email.com", "Egypt", "Suspended", "AH", "Bachelor's", "Harvard", "Medicine", "+20 100 456789", (now - timedelta(days=200)).strftime("%Y-%m-%d"), (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M"), 0, 2),
        ("Li Wei", "li.wei@email.com", "China", "Active", "LW", "PhD", "University of Tokyo", "Physics", "+86 138 0000", (now - timedelta(days=45)).strftime("%Y-%m-%d"), (now - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"), 4, 6),
    ]
    cur.executemany(
        """INSERT INTO students
        (name, email, country, status, avatar, degree_level, university_interest,
         field_of_study, phone, registered_on, last_login, total_applications, saved_scholarships)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        students,
    )


def seed_applications(cur):
    apps = [
        (1, 1, "Pending"),
        (2, 1, "Under Review"),
        (1, 2, "Approved"),
        (3, 3, "Pending"),
        (5, 5, "Rejected"),
        (2, 4, "Under Review"),
    ]
    now = datetime.now()
    for i, (sch_id, stu_id, status) in enumerate(apps):
        applied = (now - timedelta(days=i * 3)).strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO applications (scholarship_id, student_id, status, applied_on) VALUES (?, ?, ?, ?)",
            (sch_id, stu_id, status, applied),
        )


def seed_notifications(cur):
    now = datetime.now()
    notes = [
        ("New scholarship added", "DAAD Scholarship Program 2025 has been published.", "plus-circle", now - timedelta(minutes=15)),
        ("Application approved", "James Wilson's Chevening application was approved.", "check-circle", now - timedelta(hours=2)),
        ("Student registered", "Li Wei joined Scholarship Bridge.", "user-plus", now - timedelta(hours=5)),
        ("Deadline reminder", "Chevening Scholarship closes in 30 days.", "clock", now - timedelta(days=1)),
        ("Database backup completed", "Scheduled backup finished successfully.", "database", now - timedelta(days=2)),
    ]
    for title, message, icon, ts in notes:
        cur.execute(
            "INSERT INTO notifications (title, message, icon, created_at) VALUES (?, ?, ?, ?)",
            (title, message, icon, ts.strftime("%Y-%m-%d %H:%M")),
        )


def get_dashboard_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM scholarships")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'Open'")
    active = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'Closing Soon'")
    closing = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'Closed'")
    expired = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students")
    students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applications")
    applications = cur.fetchone()[0]

    conn.close()
    return {
        "total_scholarships": total,
        "active_scholarships": active,
        "closing_soon": closing,
        "expired_scholarships": expired,
        "registered_students": students,
        "total_applications": applications,
    }
