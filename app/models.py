import sqlite3
import os
from werkzeug.security import generate_password_hash


DATABASE = "database/paperguard.db"


def get_db():
    os.makedirs("database", exist_ok=True)

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    db = get_db()

    # ---------------- USERS TABLE ----------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # ---------------- PAPERS TABLE ----------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            uploaded_by INTEGER,
            assigned_to INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------- DATABASE MIGRATION ----------------
    # Add assigned_to if the old database doesn't have it

    columns = db.execute(
        "PRAGMA table_info(papers)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "assigned_to" not in column_names:

        db.execute("""
            ALTER TABLE papers
            ADD COLUMN assigned_to INTEGER
        """)

    # ---------------- ACCESS LOGS ----------------

    db.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            paper_id INTEGER,
            action TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------- ADMIN ----------------

    admin = db.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if not admin:

        db.execute(
            """
            INSERT INTO users
            (username, password, role)
            VALUES (?, ?, ?)
            """,
            (
                "admin",
                generate_password_hash(
                    "admin123",
                    method="pbkdf2:sha256"
                ),
                "admin"
            )
        )

    # ---------------- DEFAULT FACULTY ----------------

    faculty = db.execute(
        "SELECT * FROM users WHERE username = ?",
        ("faculty",)
    ).fetchone()

    if not faculty:

        db.execute(
            """
            INSERT INTO users
            (username, password, role)
            VALUES (?, ?, ?)
            """,
            (
                "faculty",
                generate_password_hash(
                    "faculty123",
                    method="pbkdf2:sha256"
                ),
                "faculty"
            )
        )

    db.commit()
    db.close()