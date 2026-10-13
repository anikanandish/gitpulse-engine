from datetime import datetime, timezone
import hashlib
import hmac
import json
import logging
import os
from fastapi import FastAPI, HTTPException, Request, status

# Configure file logging
logging.basicConfig(
    filename="events.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="GitPulse Webhook Engine")

# Webhook secret key configuration (from environment)
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET") or os.getenv("WEBHOOK_SECRET")


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


# In-memory telemetry counter
telemetry_data = {
    "total_events": 0,
    "pushes": 0,
    "pull_requests": 0,
    "repositories": {}
}

@app.get("/")
def home():
    return {
        "app": "GitPulse Engine",
        "status": "healthy",
        "version": "0.1.0",
        "endpoints": {
            "webhook": "/webhook",
            "metrics": "/metrics",
            "reset_metrics": "/metrics/reset"
        }
    }

@app.get("/metrics")
def get_metrics():
    return {
        "telemetry": telemetry_data,
        "status": "recording",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# --- METRICS RESET ROUTE ---
@app.post("/metrics/reset")
def reset_metrics():
    telemetry_data["total_events"] = 0
    telemetry_data["pushes"] = 0
    telemetry_data["pull_requests"] = 0
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
    
    if event_type == "push":
        telemetry_data["pushes"] += 1
        pusher = payload.get("pusher", {}).get("name", "Unknown")
        repo = payload.get("repository", {}).get("name", "Unknown")
        commits = payload.get("commits", [])
        commit_count = len(commits)
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
        telemetry_data["pull_requests"] += 1
        repo = payload.get("repository", {}).get("name", "Unknown")
        if repo not in telemetry_data["repositories"]:
            telemetry_data["repositories"][repo] = {"pushes": 0, "pull_requests": 0}
        telemetry_data["repositories"][repo]["pull_requests"] += 1
        action = payload.get("action", "")
        pr_title = payload.get("pull_request", {}).get("title", "")
        author = payload.get("sender", {}).get("login", "")
        logging.info(f"PR '{pr_title}' ({action}) by {author}")
        print(f" Action: {action}")
        print(f" PR Title: {pr_title}")
        print(f" Author: {author}")
        
    return {
        "status": "success",
        "event": event_type,
        "recorded_events_total": telemetry_data["total_events"]
    }