# GitPulse Engine 

An event-driven telemetry and analytics receiver designed to ingest, process, and track real-time GitHub repository events and workflow metrics.

A real-time GitHub webhook receiver and telemetry pipeline built with Python and FastAPI.
---

## Overview

**GitPulse Engine** provides automated repository telemetry by capturing live GitHub Webhook events. It acts as the core ingestion pipeline to track commit frequency, pull request cycle times, and build health metrics for continuous integration monitoring.

---

## Features

- **Real-Time Webhook Processing**: Catches and inspects asynchronous GitHub webhook payloads (`push`, `pull_request`, workflow events).
- **Lightweight Architecture**: Built with **FastAPI** and **Uvicorn** for high-throughput, low-latency request handling.
- **Event Dispatching**: Extracts commit logs, author metadata, repository details, and PR states for downstream database aggregation.

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

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/anikanandish/gitpulse-engine.git](https://github.com/anikanandish/gitpulse-engine.git)
   cd gitpulse-engine
