from datetime import datetime, timezone
import hashlib
import hmac
import json
import logging
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response

# Configure file logging
logging.basicConfig(
    filename="events.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="GitPulse Webhook Engine")

import dashboard
import db
import notifier

# Webhook secret key configuration (from environment)
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET") or os.getenv("WEBHOOK_SECRET")
MAX_PAYLOAD_SIZE = int(os.getenv("MAX_PAYLOAD_SIZE", 2 * 1024 * 1024))  # 2MB default max


def verify_signature(payload_body: bytes, signature_header: str | None) -> bool:
    """Validate X-Hub-Signature-256 against raw request payload using HMAC SHA-256."""
    if not WEBHOOK_SECRET:
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256
    ).hexdigest()

    received_signature = signature_header[len("sha256="):]
    return hmac.compare_digest(expected_signature, received_signature)


# Database and persistent telemetry initialization
db.init_db()
telemetry_data = db.load_metrics()
SERVER_START_TIME = datetime.now(timezone.utc)


def get_uptime_seconds() -> float:
    """Calculate process uptime in seconds."""
    return round((datetime.now(timezone.utc) - SERVER_START_TIME).total_seconds(), 2)


@app.get("/")
def home():
    return {
        "app": "GitPulse Engine",
        "status": "healthy",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "dashboard": "/dashboard",
            "webhook": "/webhook",
            "metrics": "/metrics",
            "reset_metrics": "/metrics/reset",
            "events": "/events",
            "events_export": "/events/export?format=json|csv",
            "event_detail": "/events/{event_id}",
            "replay_event": "/events/{event_id}/replay",
            "dlq": "/dlq",
            "dlq_clear": "/dlq/clear"
        }
    }


@app.get("/health")
def health_check():
    """System health check, uptime, and database connectivity status."""
    uptime_sec = get_uptime_seconds()
    db_status = db.check_health()
    is_healthy = db_status.get("database") == "connected"
    return {
        "status": "healthy" if is_healthy else "degraded",
        "app": "GitPulse Engine",
        "version": "0.1.0",
        "uptime_seconds": uptime_sec,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/dashboard", response_class=HTMLResponse)
def view_dashboard():
    """Render real-time telemetry dashboard UI."""
    return HTMLResponse(content=dashboard.get_dashboard_html())

@app.get("/metrics")
def get_metrics():
    return {
        "telemetry": telemetry_data,
        "status": "recording",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/events")
def get_events(
    event_type: Optional[str] = None,
    repository: Optional[str] = None,
    sender: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    return db.get_events(
        event_type=event_type,
        repository=repository,
        sender=sender,
        since=since,
        until=until,
        limit=limit,
        offset=offset
    )


@app.get("/events/export")
def export_events(
    format: str = "json",
    event_type: Optional[str] = None,
    repository: Optional[str] = None
):
    """Export stored webhook events in CSV or JSON format."""
    format_lower = format.lower().strip()
    if format_lower == "csv":
        csv_data = db.export_events_csv(event_type=event_type, repository=repository)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=gitpulse-events.csv"}
        )
    elif format_lower == "json":
        data = db.get_events(event_type=event_type, repository=repository, limit=10000)
        return {
            "export_format": "json",
            "total_count": data.get("total", 0),
            "events": data.get("events", [])
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{format}'. Supported formats: csv, json."
        )


@app.get("/events/{event_id}")
def get_single_event(event_id: int):
    event = db.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found"
        )
    return event

@app.post("/events/{event_id}/replay")
def replay_event(event_id: int):
    """Replay an existing event and re-trigger notifications without re-ingesting."""
    event = db.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found"
        )
    notifier.dispatch_notifications(
        event_type=event["event_type"],
        summary=f"[REPLAY] {event['summary']}",
        details={"repository": event["repository"], "sender": event["sender"], "event_id": event_id}
    )
    logging.info(f"Replayed event {event_id}: {event['summary']}")
    return {
        "status": "replayed",
        "event_id": event_id,
        "event_type": event["event_type"],
        "summary": event["summary"]
    }

@app.get("/dlq")
def get_dead_letter_queue(limit: int = 50):
    """Inspect dead-letter queue records for failed event/notification deliveries."""
    items = db.get_dlq_events(limit=limit)
    return {
        "dlq": items,
        "count": len(items),
        "limit": limit
    }

@app.post("/dlq/clear")
def clear_dead_letter_queue():
    """Clear all records from Dead-Letter Queue."""
    deleted = db.clear_dlq()
    return {
        "message": f"Cleared {deleted} entries from Dead-Letter Queue",
        "cleared_count": deleted
    }

# --- METRICS RESET ROUTE ---
@app.post("/metrics/reset")
def reset_metrics():
    global telemetry_data
    db.reset_db()
    telemetry_data = {
        "total_events": 0,
        "pushes": 0,
        "pull_requests": 0,
        "issues": 0,
        "workflow_runs": 0,
        "releases": 0,
        "repositories": {}
    }
    logging.info("Telemetry metrics reset to zero")
    return {"message": "Telemetry metrics reset successfully", "telemetry": telemetry_data}

@app.post("/webhook")
async def receive_github_webhook(request: Request):
    payload_body = await request.body()
    github_signature = request.headers.get("X-Hub-Signature-256")

    if WEBHOOK_SECRET:
        if not github_signature or not verify_signature(payload_body, github_signature):
            logging.warning("Rejected webhook: invalid or missing HMAC signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing X-Hub-Signature-256 signature"
            )
    elif not github_signature:
        logging.warning("Received webhook without X-Hub-Signature-256 header (WEBHOOK_SECRET not set)")

    try:
        payload = json.loads(payload_body) if payload_body else {}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    
    # Increment total event counter
    telemetry_data["total_events"] += 1
    
    # Log incoming event type to events.log
    logging.info(f"Incoming GitHub event: {event_type}")

    print("\n" + "=" * 45)
    print(f" RECEIVED GITHUB EVENT: {event_type.upper()}")
    print("=" * 45)
    
    summary = f"GitHub event {event_type}"
    repo = payload.get("repository", {}).get("name", "Unknown") if isinstance(payload.get("repository"), dict) else "Unknown"
    sender = payload.get("sender", {}).get("login", "Unknown") if isinstance(payload.get("sender"), dict) else "Unknown"

    if event_type == "push":
        telemetry_data["pushes"] += 1
        pusher = payload.get("pusher", {}).get("name", sender)
        commits = payload.get("commits", [])
        commit_count = len(commits)
        summary = f"Push with {commit_count} commits by {pusher}"
        if repo not in telemetry_data["repositories"]:
            telemetry_data["repositories"][repo] = {"pushes": 0, "pull_requests": 0}
        telemetry_data["repositories"][repo]["pushes"] += 1
        distinct_authors = len({c.get("author", {}).get("username") for c in commits if c.get("author", {}).get("username")})
        
        logging.info(f"Push by {pusher} in {repo} with {commit_count} commits across {distinct_authors} authors")
        print(f" Pusher: {pusher}")
        print(f" Repo: {repo}")
        print(f" Total Commits: {commit_count} (Unique Authors: {distinct_authors})")
        for c in commits:
            print(f"   - {c.get('message')}")
            
    elif event_type == "pull_request":
        telemetry_data["pull_requests"] = telemetry_data.get("pull_requests", 0) + 1
        if repo not in telemetry_data["repositories"]:
            telemetry_data["repositories"][repo] = {"pushes": 0, "pull_requests": 0, "issues": 0, "workflow_runs": 0}
        telemetry_data["repositories"][repo]["pull_requests"] = telemetry_data["repositories"][repo].get("pull_requests", 0) + 1
        action = payload.get("action", "")
        pr_title = payload.get("pull_request", {}).get("title", "")
        author = payload.get("sender", {}).get("login", sender)
        summary = f"PR '{pr_title}' ({action}) by {author}"
        logging.info(f"PR '{pr_title}' ({action}) by {author}")
        print(f" Action: {action}")
        print(f" PR Title: {pr_title}")
        print(f" Author: {author}")

    elif event_type == "issues":
        telemetry_data["issues"] = telemetry_data.get("issues", 0) + 1
        if repo not in telemetry_data["repositories"]:
            telemetry_data["repositories"][repo] = {"pushes": 0, "pull_requests": 0, "issues": 0, "workflow_runs": 0}
        telemetry_data["repositories"][repo]["issues"] = telemetry_data["repositories"][repo].get("issues", 0) + 1
        action = payload.get("action", "")
        issue_title = payload.get("issue", {}).get("title", "")
        issue_num = payload.get("issue", {}).get("number", "")
        summary = f"Issue #{issue_num} '{issue_title}' ({action}) by {sender}"
        logging.info(summary)
        print(f" Action: {action}")
        print(f" Issue: #{issue_num} {issue_title}")

    elif event_type == "workflow_run":
        telemetry_data["workflow_runs"] = telemetry_data.get("workflow_runs", 0) + 1
        if repo not in telemetry_data["repositories"]:
            telemetry_data["repositories"][repo] = {"pushes": 0, "pull_requests": 0, "issues": 0, "workflow_runs": 0}
        telemetry_data["repositories"][repo]["workflow_runs"] = telemetry_data["repositories"][repo].get("workflow_runs", 0) + 1
        wf_name = payload.get("workflow_run", {}).get("name", "Unknown Workflow")
        wf_conclusion = payload.get("workflow_run", {}).get("conclusion") or payload.get("workflow_run", {}).get("status", "running")
        branch = payload.get("workflow_run", {}).get("head_branch", "unknown")
        summary = f"Workflow '{wf_name}' [{str(wf_conclusion).upper()}] on branch {branch}"
        logging.info(summary)
        print(f" Workflow: {wf_name}")
        print(f" Status: {wf_conclusion}")
        print(f" Branch: {branch}")

    elif event_type == "release":
        telemetry_data["releases"] = telemetry_data.get("releases", 0) + 1
        tag = payload.get("release", {}).get("tag_name", "unversioned")
        action = payload.get("action", "published")
        summary = f"Release {tag} ({action}) by {sender}"
        logging.info(summary)
        print(f" Release: {tag} ({action})")

    elif event_type == "ping":
        zen = payload.get("zen", "Keep it logically awesome.")
        summary = f"GitHub webhook ping (zen: {zen})"
        logging.info(summary)
        print(f" Ping Zen: {zen}")

    event_id = db.save_event(
        event_type=event_type,
        repository=repo,
        sender=sender,
        summary=summary,
        payload=payload
    )

    notifier.dispatch_notifications(
        event_type=event_type,
        summary=summary,
        details={"repository": repo, "sender": sender, "event_id": event_id}
    )

    return {
        "status": "success",
        "event": event_type,
        "event_id": event_id,
        "recorded_events_total": telemetry_data["total_events"]
    }