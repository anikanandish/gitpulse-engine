from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_FILE = os.getenv("GITPULSE_DB_FILE", "gitpulse.db")


@contextmanager
def get_connection(db_path: str = DB_FILE):
    """Context manager for SQLite connections that ensures proper closure."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: str = DB_FILE) -> None:
    """Initialize database tables and indexes."""
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                repository TEXT NOT NULL,
                sender TEXT NOT NULL,
                summary TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_repo ON events(repository)")
        conn.commit()


def save_event(
    event_type: str,
    repository: str,
    sender: str,
    summary: str,
    payload: Dict[str, Any],
    created_at: Optional[str] = None,
    db_path: str = DB_FILE
) -> int:
    """Persist an event to the database and return its new row ID."""
    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()
    payload_json = json.dumps(payload)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (event_type, repository, sender, summary, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event_type, repository, sender, summary, payload_json, created_at)
        )
        conn.commit()
        return cursor.lastrowid


def load_metrics(db_path: str = DB_FILE) -> Dict[str, Any]:
    """Calculate aggregated telemetry metrics from persisted event records."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'push'")
        pushes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'pull_request'")
        pull_requests = cursor.fetchone()[0]

        cursor.execute("""
            SELECT repository,
                   SUM(CASE WHEN event_type = 'push' THEN 1 ELSE 0 END) as push_count,
                   SUM(CASE WHEN event_type = 'pull_request' THEN 1 ELSE 0 END) as pr_count
            FROM events
            WHERE repository != 'Unknown'
            GROUP BY repository
        """)
        repositories = {}
        for row in cursor.fetchall():
            repositories[row["repository"]] = {
                "pushes": row["push_count"],
                "pull_requests": row["pr_count"]
            }

        return {
            "total_events": total_events,
            "pushes": pushes,
            "pull_requests": pull_requests,
            "repositories": repositories
        }


def get_recent_events(limit: int = 20, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve recent recorded events."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, event_type, repository, sender, summary, created_at
            FROM events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "event_type": row["event_type"],
                "repository": row["repository"],
                "sender": row["sender"],
                "summary": row["summary"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]


def reset_db(db_path: str = DB_FILE) -> None:
    """Clear all events from database."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM events")
        conn.commit()
