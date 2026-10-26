import hashlib
import hmac
import json
import os
import unittest
from fastapi.testclient import TestClient

import db
import gitpulse

class GitPulseTestCase(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_unit.db"
        db.DB_FILE = self.test_db
        db.init_db(self.test_db)
        gitpulse.WEBHOOK_SECRET = "test_secret_key"
        self.client = TestClient(gitpulse.app)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        if os.path.exists("events.log"):
            try:
                os.remove("events.log")
            except OSError:
                pass

    def test_home_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("analytics_leaderboard", data["endpoints"])
        self.assertIn("events_search", data["endpoints"])

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("uptime_seconds", data)
        self.assertEqual(data["database"]["database"], "connected")

    def test_metrics_endpoint(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "recording")
        self.assertIn("telemetry", data)

    def test_analytics_leaderboard(self):
        db.save_event("push", "repo-1", "user-a", "test push 1", {}, db_path=self.test_db)
        db.save_event("push", "repo-1", "user-b", "test push 2", {}, db_path=self.test_db)
        db.save_event("issues", "repo-2", "user-a", "test issue 1", {}, db_path=self.test_db)

        response = self.client.get("/analytics/leaderboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        analytics = data["analytics"]
        self.assertEqual(analytics["top_repositories"][0]["repository"], "repo-1")
        self.assertEqual(analytics["top_repositories"][0]["events_count"], 2)
        self.assertEqual(analytics["top_senders"][0]["sender"], "user-a")
        self.assertEqual(analytics["top_senders"][0]["events_count"], 2)

    def test_events_search(self):
        db.save_event("push", "backend", "alice", "fix: database connection leak", {}, db_path=self.test_db)
        db.save_event("pull_request", "frontend", "bob", "feat: dark mode theme", {}, db_path=self.test_db)

        res = self.client.get("/events/search?q=connection")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_matches"], 1)
        self.assertEqual(data["results"][0]["repository"], "backend")

        empty_res = self.client.get("/events/search?q=")
        self.assertEqual(empty_res.status_code, 400)

    def test_events_export_csv_and_json(self):
        db.save_event("push", "core-repo", "charlie", "commit 123", {}, db_path=self.test_db)

        csv_res = self.client.get("/events/export?format=csv")
        self.assertEqual(csv_res.status_code, 200)
        self.assertIn("text/csv", csv_res.headers["content-type"])
        self.assertIn("core-repo", csv_res.text)

        json_res = self.client.get("/events/export?format=json")
        self.assertEqual(json_res.status_code, 200)
        data = json_res.json()
        self.assertEqual(data["export_format"], "json")
        self.assertGreaterEqual(data["total_count"], 1)

    def test_webhook_hmac_signature_validation(self):
        payload = json.dumps({"action": "opened", "issue": {"title": "Bug in API"}}).encode("utf-8")
        secret = "test_secret_key"
        signature = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        # Valid signature
        headers = {
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "issues",
            "Content-Type": "application/json"
        }
        res = self.client.post("/webhook", content=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["event"], "issues")

        # Invalid signature
        bad_headers = {
            "X-Hub-Signature-256": "sha256=invalid_signature_hex",
            "X-GitHub-Event": "issues",
            "Content-Type": "application/json"
        }
        bad_res = self.client.post("/webhook", content=payload, headers=bad_headers)
        self.assertEqual(bad_res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
