import logging
from fastapi import FastAPI, Request

# Configure file logging
logging.basicConfig(
    filename="events.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="GitPulse Webhook Engine")

# In-memory telemetry counter
telemetry_data = {
    "total_events": 0,
    "pushes": 0,
    "pull_requests": 0
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
        "status": "recording"
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
    github_signature = request.headers.get("X-Hub-Signature-256")
    if not github_signature:
        logging.warning("Received webhook without X-Hub-Signature-256 header")

    payload = await request.json()
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
        distinct_authors = len({c.get("author", {}).get("username") for c in commits if c.get("author", {}).get("username")})
        
        logging.info(f"Push by {pusher} in {repo} with {commit_count} commits across {distinct_authors} authors")
        print(f" Pusher: {pusher}")
        print(f" Repo: {repo}")
        print(f" Total Commits: {commit_count} (Unique Authors: {distinct_authors})")
        for c in commits:
            print(f"   - {c.get('message')}")
            
    elif event_type == "pull_request":
        telemetry_data["pull_requests"] += 1
        action = payload.get("action", "")
        pr_title = payload.get("pull_request", {}).get("title", "")
        author = payload.get("sender", {}).get("login", "")
        logging.info(f"PR '{pr_title}' ({action}) by {author}")
        print(f" Action: {action}")
        print(f" PR Title: {pr_title}")
        print(f" Author: {author}")
        
    return {"message": "Event received successfully!"}