import json
import urllib.request

url = "http://127.0.0.1:8000/webhook"
headers = {
    "Content-Type": "application/json",
    "X-GitHub-Event": "push"
}

with open("tests/sample_push.json", "r") as f:
    data = json.load(f)

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers=headers,
    method="POST"
)

with urllib.request.urlopen(req) as response:
    print("Response Code:", response.status)
    print("Response Body:", response.read().decode("utf-8"))