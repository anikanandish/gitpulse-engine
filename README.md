# GitPulse Engine 

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)
![License-MIT](https://img.shields.io/badge/License-MIT-yellow)

> A lightweight, event-driven GitHub telemetry receiver and metric aggregator built with FastAPI.

An event-driven telemetry and analytics receiver designed to ingest, process, and track real-time GitHub repository events and workflow metrics.

A real-time GitHub webhook receiver and telemetry pipeline built with Python and FastAPI.
---


## API Endpoints

- `GET /` — Engine health status, version, and route index
- `GET /metrics` — Live in-memory telemetry aggregates (total events, pushes, PRs)
- `POST /webhook` — GitHub webhook payload ingestion listener

## Overview

**GitPulse Engine** provides automated repository telemetry by capturing live GitHub Webhook events. It acts as the core ingestion pipeline to track commit frequency, pull request cycle times, and build health metrics for continuous integration monitoring.

---

## Features

- **Real-Time Webhook Processing**: Catches and inspects asynchronous GitHub webhook payloads (`push`, `pull_request`, workflow events).
- **Lightweight Architecture**: Built with **FastAPI** and **Uvicorn** for high-throughput, low-latency request handling.
- **Event Dispatching**: Extracts commit logs, author metadata, repository details, and PR states for downstream database aggregation.

---
## Local Testing

To simulate GitHub events locally without configuring an external tunnel:

```powershell
# In terminal 1: Start the engine
uvicorn gitpulse:app --reload --port 8000

# In terminal 2: Trigger a simulated push event
python test_webhook.py

---
## Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Integration**: GitHub Webhooks, Git
- **Storage & Infrastructure** *(In Progress)*: PostgreSQL, Docker

---

## Future implimenation


## Getting Started

### Prerequisites

- Python 3.10+
- Git
- `pip` package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/anikanandish/gitpulse-engine.git](https://github.com/anikanandish/gitpulse-engine.git)
   cd gitpulse-engine


---

## Roadmap

- [x] In-memory telemetry counter & metrics endpoint
- [x] Local mock event test runner
- [ ] HMAC SHA-256 signature verification for webhook payloads
- [ ] SQLite persistence layer for event history
- [ ] Discord / Slack notification dispatcher

## Architecture Flow
