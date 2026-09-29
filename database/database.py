"""SQLite persistence for users, assessments, and calculated carbon results."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent / "sustainable.db"


@contextmanager
def _connect(db_path: str | Path = DEFAULT_DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(str(db_path), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(db_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
    """Create the local schema if it does not already exist."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                assessment_date TEXT NOT NULL,
                lifestyle_data_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS carbon_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL UNIQUE REFERENCES assessments(id) ON DELETE CASCADE,
                transport_co2 REAL NOT NULL,
                energy_co2 REAL NOT NULL,
                diet_co2 REAL NOT NULL,
                shopping_co2 REAL NOT NULL,
                waste_co2 REAL NOT NULL,
                total_co2 REAL NOT NULL,
                sustainability_score REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_assessments_user_date
                ON assessments(user_id, assessment_date);
            """
        )


def save_assessment(
    name: str,
    email: str,
    lifestyle_data: Mapping[str, Any],
    carbon_results: Mapping[str, float],
    sustainability_score: float,
    db_path: str | Path = DEFAULT_DATABASE_PATH,
) -> tuple[int, str]:
    """Persist one validated assessment and its category results."""
    initialize_database(db_path)
    assessment_date = datetime.now(timezone.utc).isoformat(timespec="seconds")
    normalized_email = email.strip().lower()
    with _connect(db_path) as connection:
        connection.execute(
            """INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)
               ON CONFLICT(email) DO UPDATE SET name = excluded.name""",
            (name.strip(), normalized_email, assessment_date),
        )
        user = connection.execute("SELECT id FROM users WHERE email = ?", (normalized_email,)).fetchone()
        if user is None:
            raise sqlite3.DatabaseError("Unable to create or retrieve the assessment user.")
        cursor = connection.execute(
            """INSERT INTO assessments (user_id, assessment_date, lifestyle_data_json)
               VALUES (?, ?, ?)""",
            (user["id"], assessment_date, json.dumps(dict(lifestyle_data), allow_nan=False)),
        )
        assessment_id = int(cursor.lastrowid)
        connection.execute(
            """INSERT INTO carbon_results (
                   assessment_id, transport_co2, energy_co2, diet_co2, shopping_co2,
                   waste_co2, total_co2, sustainability_score
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                assessment_id,
                carbon_results["transport"],
                carbon_results["energy"],
                carbon_results["diet"],
                carbon_results["shopping"],
                carbon_results["waste"],
                carbon_results["total"],
                sustainability_score,
            ),
        )
    return assessment_id, assessment_date


def get_assessment_history(
    email: str,
    db_path: str | Path = DEFAULT_DATABASE_PATH,
) -> list[dict[str, Any]]:
    """Return an email-keyed user's assessments in chronological order."""
    initialize_database(db_path)
    with _connect(db_path) as connection:
        rows = connection.execute(
            """SELECT a.id AS assessment_id, a.assessment_date, a.lifestyle_data_json,
                      c.transport_co2, c.energy_co2, c.diet_co2, c.shopping_co2,
                      c.waste_co2, c.total_co2, c.sustainability_score
               FROM assessments AS a
               JOIN users AS u ON u.id = a.user_id
               JOIN carbon_results AS c ON c.assessment_id = a.id
               WHERE lower(u.email) = lower(?)
               ORDER BY a.assessment_date, a.id""",
            (email.strip(),),
        ).fetchall()
    return [dict(row) for row in rows]


def get_latest_assessment(
    email: str,
    db_path: str | Path = DEFAULT_DATABASE_PATH,
) -> dict[str, Any] | None:
    """Return the latest assessment for an email, or ``None`` if none exists."""
    history = get_assessment_history(email, db_path)
    return history[-1] if history else None