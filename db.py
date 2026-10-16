from contextlib import contextmanager
import csv
from datetime import datetime, timezone
import io
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_FILE = os.getenv("GITPULSE_DB_FILE", "gitpulse.db")


def get_db_path(db_path: Optional[str] = None) -> str:
    """Resolve active database path dynamically."""
    return db_path or DB_FILE


@contextmanager
def get_connection(db_path: Optional[str] = None):
    """Context manager for SQLite connections that ensures proper closure."""
    conn = sqlite3.connect(get_db_path(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dlq_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                event_type TEXT NOT NULL,
                channel TEXT NOT NULL,
                error_reason TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_repo ON events(repository)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dlq_type ON dlq_events(event_type)")
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

        cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'issues'")
        issues = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'workflow_run'")
        workflow_runs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'release'")
        releases = cursor.fetchone()[0]

        cursor.execute("""
            SELECT repository,
                   SUM(CASE WHEN event_type = 'push' THEN 1 ELSE 0 END) as push_count,
                   SUM(CASE WHEN event_type = 'pull_request' THEN 1 ELSE 0 END) as pr_count,
                   SUM(CASE WHEN event_type = 'issues' THEN 1 ELSE 0 END) as issue_count,
                   SUM(CASE WHEN event_type = 'workflow_run' THEN 1 ELSE 0 END) as workflow_count
            FROM events
            WHERE repository != 'Unknown'
            GROUP BY repository
        """)
        repositories = {}
        for row in cursor.fetchall():
            repositories[row["repository"]] = {
                "pushes": row["push_count"],
                "pull_requests": row["pr_count"],
                "issues": row["issue_count"],
                "workflow_runs": row["workflow_count"]
            }

        return {
            "total_events": total_events,
            "pushes": pushes,
            "pull_requests": pull_requests,
            "issues": issues,
            "workflow_runs": workflow_runs,
            "releases": releases,
            "repositories": repositories
        }


def get_events(
    event_type: Optional[str] = None,
    repository: Optional[str] = None,
    sender: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db_path: str = DB_FILE
) -> Dict[str, Any]:
    """Retrieve filtered, paginated events."""
    init_db(db_path)
    conditions = []
    params: List[Any] = []

    if event_type:
        conditions.append("event_type = ?")
        params.append(event_type)
    if repository:
        conditions.append("repository = ?")
        params.append(repository)
    if sender:
        conditions.append("sender = ?")
        params.append(sender)
    if since:
        conditions.append("created_at >= ?")
        params.append(since)
    if until:
        conditions.append("created_at <= ?")
        params.append(until)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM events {where_clause}", params)
        total_matching = cursor.fetchone()[0]

        cursor.execute(
            f"""
            SELECT id, event_type, repository, sender, summary, created_at
            FROM events
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset]
        )
        rows = cursor.fetchall()
        items = [
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
        return {
            "total": total_matching,
            "limit": limit,
            "offset": offset,
            "events": items
        }


def get_event_by_id(event_id: int, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """Retrieve a single event and its parsed payload by ID."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, event_type, repository, sender, summary, payload, created_at FROM events WHERE id = ?",
            (event_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "event_type": row["event_type"],
            "repository": row["repository"],
            "sender": row["sender"],
            "summary": row["summary"],
            "payload": json.loads(row["payload"]) if row["payload"] else {},
            "created_at": row["created_at"]
        }


def get_recent_events(limit: int = 20, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve recent recorded events (convenience wrapper)."""
    return get_events(limit=limit, db_path=db_path)["events"]


def reset_db(db_path: str = DB_FILE) -> None:
    """Clear all events and DLQ entries from database."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM events")
        conn.execute("DELETE FROM dlq_events")
        conn.commit()


def record_dlq(
    event_type: str,
    payload: Dict[str, Any],
    error_reason: str,
    channel: str = "general",
    event_id: Optional[int] = None,
    created_at: Optional[str] = None,
    db_path: str = DB_FILE
) -> int:
    """Record an unhandled or failed delivery event to the Dead-Letter Queue."""
    init_db(db_path)
    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()
    payload_json = json.dumps(payload)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO dlq_events (event_id, event_type, channel, error_reason, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event_id, event_type, channel, error_reason, payload_json, created_at)
        )
        conn.commit()
        return cursor.lastrowid


def get_dlq_events(limit: int = 50, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieve items from the Dead-Letter Queue."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, event_id, event_type, channel, error_reason, payload, created_at
            FROM dlq_events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "channel": row["channel"],
                "error_reason": row["error_reason"],
                "payload": json.loads(row["payload"]) if row["payload"] else {},
                "created_at": row["created_at"],
            }
            for row in rows
        ]


def clear_dlq(db_path: str = DB_FILE) -> int:
    """Clear all records from Dead-Letter Queue."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dlq_events")
        deleted = cursor.rowcount
        conn.commit()
        return deleted


def check_health(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Verify SQLite database connectivity and return basic stats."""
    try:
        init_db(db_path)
        with get_connection(db_path) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM events")
            total_events = cur.fetchone()[0]
            cur = conn.execute("SELECT COUNT(*) FROM dlq_events")
            total_dlq = cur.fetchone()[0]
            return {
                "database": "connected",
                "events_count": total_events,
                "dlq_count": total_dlq
            }
    except Exception as e:
        return {
            "database": "unhealthy",
            "error": str(e)
        }


def export_events_csv(
    event_type: Optional[str] = None,
    repository: Optional[str] = None,
    db_path: str = DB_FILE
) -> str:
    """Export stored events as RFC 4180 compliant CSV string."""
    init_db(db_path)
    events_data = get_events(event_type=event_type, repository=repository, limit=10000, db_path=db_path)
    items = events_data.get("events", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "event_type", "repository", "sender", "summary", "created_at"])
    for item in items:
        writer.writerow([
            item.get("id"),
            item.get("event_type"),
            item.get("repository"),
            item.get("sender"),
            item.get("summary"),
            item.get("created_at")
        ])
    return output.getvalue()


