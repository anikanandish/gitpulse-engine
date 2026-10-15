import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def _post_json(url: str, data: Dict[str, Any], timeout: float = 3.0) -> bool:
    """Send a JSON POST request to a webhook URL with a timeout."""
    try:
        body = json.dumps(data).encode("utf-8")
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
            return response.status in (200, 204)
    except Exception as e:
        logging.error(f"Failed to deliver notification to {url}: {e}")
        try:
            import db
            db.record_dlq(
                event_type="notification_failure",
                payload={"target_url": url, "notification_payload": data},
                error_reason=str(e),
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
