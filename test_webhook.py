import json
import os
import sys
import urllib.request
import urllib.error

def send_test_webhook(event_type="push", host="http://127.0.0.1:8000"):
    fixture_map = {
        "push": "tests/sample_push.json",
        "pull_request": "tests/sample_pull_request.json",
    }
    
    fixture_path = fixture_map.get(event_type, f"tests/sample_{event_type}.json")
    if not os.path.exists(fixture_path):
        print(f"Error: Fixture file not found: {fixture_path}")
        return

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    payload_bytes = json.dumps(data).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": event_type,
    }

    url = f"{host.rstrip('/')}/webhook"
    req = urllib.request.Request(
        url,
        data=payload_bytes,
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            print("Response Code:", response.status)
            print("Response Body:", response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"Connection Error: {e.reason}. Is the server running at {url}?")

if __name__ == "__main__":
    event = sys.argv[1] if len(sys.argv) > 1 else "push"
    send_test_webhook(event)