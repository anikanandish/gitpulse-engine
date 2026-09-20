import logging
from fastapi import FastAPI, Request

# Configure file logging
logging.basicConfig(
    filename="events.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="GitPulse Webhook Engine")

@app.get("/")
def home():
    return {
        "app": "GitPulse Engine",
        "status": "healthy",
        "version": "0.1.0",
        "endpoints": {
            "webhook": "/webhook"
        }
    }

@app.post("/webhook")
async def receive_github_webhook(request: Request):

   
    github_signature = request.headers.get("X-Hub-Signature-256")
    if not github_signature:
       logging.warning("Received webhook without X-Hub-Signature-256 header")
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    
    # Log incoming event type to events.log
    logging.info(f"Incoming GitHub event: {event_type}")

    print("\n" + "=" * 45)
    print(f" RECEIVED GITHUB EVENT: {event_type.upper()}")
    print("=" * 45)
    
    if event_type == "push":
        pusher = payload.get("pusher", {}).get("name", "Unknown")
        repo = payload.get("repository", {}).get("name", "Unknown")
        commits = payload.get("commits", [])
        logging.info(f"Push by {pusher} in {repo} with {len(commits)} commits")
        print(f" Pusher: {pusher}")
        print(f" Repo: {repo}")
        print(f" Total Commits: {len(commits)}")
        for c in commits:
            print(f"   - {c.get('message')}")
            
    elif event_type == "pull_request":
        action = payload.get("action", "")
        pr_title = payload.get("pull_request", {}).get("title", "")
        author = payload.get("sender", {}).get("login", "")
        logging.info(f"PR '{pr_title}' ({action}) by {author}")
        print(f" Action: {action}")
        print(f" PR Title: {pr_title}")
        print(f" Author: {author}")
        
    return {"message": "Event received successfully!"}