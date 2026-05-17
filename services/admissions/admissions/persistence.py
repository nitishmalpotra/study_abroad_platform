import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from .schemas import StudentProfile
from .utils import sanitize_text


class PredictionRepository(Protocol):
    def save(self, profile: StudentProfile, target_programs: list[str], raw_ai_output: str) -> None: ...


class SQLitePredictionRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA foreign_keys=ON;")
        connection.execute("PRAGMA busy_timeout=5000;")
        return connection

    def init_database(self) -> None:
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TEXT NOT NULL,
                        full_name TEXT NOT NULL,
                        target_intake TEXT NOT NULL,
                        target_country TEXT NOT NULL,
                        profile_json TEXT NOT NULL,
                        target_programs TEXT NOT NULL,
                        ai_raw_output TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC)"
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise RuntimeError("Failed to initialize SQLite database.") from exc

    def save(self, profile: StudentProfile, target_programs: list[str], raw_ai_output: str) -> None:
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO predictions (
                        created_at,
                        full_name,
                        target_intake,
                        target_country,
                        profile_json,
                        target_programs,
                        ai_raw_output
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        sanitize_text(profile.full_name, max_length=120),
                        sanitize_text(profile.target_intake, max_length=40),
                        sanitize_text(profile.target_country, max_length=60),
                        json.dumps(profile.model_dump(), ensure_ascii=True),
                        " | ".join(target_programs),
                        raw_ai_output[:12000],
                    ),
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise RuntimeError("Prediction was generated but could not be saved to SQLite.") from exc
