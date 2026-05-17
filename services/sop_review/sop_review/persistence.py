import sqlite3
from datetime import datetime, timezone

from .config import AppSettings
from .schemas import SOPGrade, StudentProfile


def get_db_connection(db_path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path, timeout=30)
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    connection.execute("PRAGMA busy_timeout=5000;")
    return connection


class SQLiteSubmissionRepository:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def init_db(self) -> None:
        with get_db_connection(self.settings.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    full_name TEXT NOT NULL,
                    university TEXT NOT NULL,
                    intake TEXT NOT NULL,
                    country TEXT NOT NULL,
                    sop_text TEXT NOT NULL,
                    overall_score REAL NOT NULL CHECK (overall_score >= 1 AND overall_score <= 10),
                    ai_feedback_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_submissions_timestamp
                ON submissions(timestamp DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_submissions_university
                ON submissions(university)
                """
            )
            connection.commit()

    def save(
        self, profile: StudentProfile, sop_text: str, grade: SOPGrade, raw_json: str
    ) -> int:
        with get_db_connection(self.settings.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO submissions (
                    timestamp, full_name, university, intake, country,
                    sop_text, overall_score, ai_feedback_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    profile.full_name,
                    profile.university,
                    profile.intake,
                    profile.country,
                    sop_text,
                    grade.overall_score,
                    raw_json,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)
