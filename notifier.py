import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
MAX_DISPATCH_RETRIES = int(os.getenv("MAX_DISPATCH_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "0.5"))


def _post_json(url: str, data: Dict[str, Any], timeout: float = 3.0, max_retries: Optional[int] = None) -> bool:
    """Send a JSON POST request with retry backoff and DLQ capture on failure."""
    retries = max_retries if max_retries is not None else MAX_DISPATCH_RETRIES
    body = json.dumps(data).encode("utf-8")
    last_error: Optional[Exception] = None

    for attempt in range(max(1, retries)):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "GitPulse-Engine/1.0"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status in (200, 204):
                    return True
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                sleep_duration = RETRY_BACKOFF_FACTOR * (2 ** attempt)
                logging.warning(
                    f"Notification attempt {attempt + 1}/{retries} to {url} failed: {e}. Retrying in {sleep_duration}s..."
                )
                time.sleep(sleep_duration)

    logging.error(f"Failed all {retries} notification delivery attempts to {url}: {last_error}")
    try:
        import db
        db.record_dlq(
            event_type="notification_failure",
            payload={"target_url": url, "notification_payload": data, "attempts": retries},
            error_reason=str(last_error),
            channel="notification"
        )
    except Exception:
        pass
    return False



def notify_discord(summary: str, details: Optional[Dict[str, Any]] = None) -> bool:
    """Dispatch alert to Discord webhook."""
    if not DISCORD_WEBHOOK_URL:
        return False

    content = f"**[GitPulse Telemetry]** {summary}"
    payload = {"content": content}
    return _post_json(DISCORD_WEBHOOK_URL, payload)


def notify_slack(summary: str, details: Optional[Dict[str, Any]] = None) -> bool:
    """Dispatch alert to Slack incoming webhook."""
    if not SLACK_WEBHOOK_URL:
        return False

    payload = {"text": f"*GitPulse Engine Alert*: {summary}"}
    return _post_json(SLACK_WEBHOOK_URL, payload)


def dispatch_notifications(event_type: str, summary: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Dispatch event notification across all configured channels."""
    if DISCORD_WEBHOOK_URL:
        notify_discord(summary, details)
    if SLACK_WEBHOOK_URL:
        notify_slack(summary, details)
