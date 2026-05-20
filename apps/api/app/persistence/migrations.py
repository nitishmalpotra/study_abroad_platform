import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .database import Database

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"


@dataclass(frozen=True)
class Migration:
    version: str
    sql: str


def load_migrations(migrations_dir: Path = MIGRATIONS_DIR) -> list[Migration]:
    migrations = []
    for path in sorted(migrations_dir.glob("*.sql")):
        migrations.append(Migration(path.stem, path.read_text(encoding="utf-8")))
    return migrations


def ensure_migration_table(cursor: Any) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def applied_versions(cursor: Any) -> set[str]:
    cursor.execute("SELECT version FROM schema_migrations")
    return {str(row[0]) for row in cursor.fetchall()}


def migration_statements(sql: str) -> list[str]:
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def apply_migrations(database: Database) -> list[str]:
    applied = []
    with database.connection() as connection:
        with connection.cursor() as cursor:
            ensure_migration_table(cursor)
            existing = applied_versions(cursor)
            for migration in load_migrations():
                if migration.version in existing:
                    continue
                for statement in migration_statements(migration.sql):
                    cursor.execute(statement)
                cursor.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (migration.version,),
                )
                applied.append(migration.version)
    return applied


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply API database migrations.")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("DATABASE_URL is required.")
    applied = apply_migrations(Database(args.database_url))
    if applied:
        print("Applied migrations: " + ", ".join(applied))
    else:
        print("No migrations to apply.")


if __name__ == "__main__":
    main()
