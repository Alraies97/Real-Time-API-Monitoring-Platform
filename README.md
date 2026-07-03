# ZA0 Live Monitor

A real-time monitoring dashboard built with FastAPI, Redis, PostgreSQL, and WebSockets. This project tracks active connections, request counts, and request latency metrics in real time. It also persists periodic metric snapshots to PostgreSQL.

## Features

- FastAPI backend with WebSocket support
- Redis-based real-time metric collection
- PostgreSQL persistence via SQLAlchemy async ORM
- Simple Tailwind-powered dashboard UI
- Load testing utility with `httpx`
- Docker Compose ready for local development and deployment

## Tech Stack

- Python 3.11
- FastAPI
- Redis
- PostgreSQL
- SQLAlchemy async
- Uvicorn
- Tailwind CSS (via CDN)
- Docker / Docker Compose

## Project Structure

- `app/main.py` — FastAPI app and WebSocket endpoint
- `app/database.py` — async SQLAlchemy engine and model
- `app/redis_client.py` — Redis async client
- `app/middleware.py` — request tracking middleware
- `app/templates/index.html` — dashboard UI
- `Dockerfile` — container image build
- `docker-compose.yml` — web, Redis, and PostgreSQL services
- `load_test.py` — async load test script

## Prerequisites

- Docker
- Docker Compose
- Python 3.11 (for local execution)

## Local Development

1. Build and start services:

```bash
docker compose up --build
```

2. Open the dashboard:

```text
http://localhost:8000
```

3. The app uses:
- Redis service at `redis://redis:6379/0`
- PostgreSQL service at `postgresql+asyncpg://postgres:postgres_password@db:5432/monitor_db`

## Run Locally without Docker

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Ensure Redis and PostgreSQL are available and matching the environment variables in `docker-compose.yml`.

## Load Testing

Use the test script to generate concurrent load against the running app:

```bash
python load_test.py
```

## Deployment Notes

- `docker-compose.yml` defines the full development stack.
- For production, remove `--reload` and mount volumes carefully.
- Secure the database credentials and Redis endpoint using environment variables.
- Replace Tailwind CDN usage with a build pipeline if static assets are preferred.

## Notes

- The WebSocket endpoint is available at `/ws/monitor`.
- The dashboard is served from `/` and reads the static HTML template directly.
- Metric snapshots are written to PostgreSQL every 10 seconds.

---

### Recommended Improvements

- Add health checks for Redis and PostgreSQL.
- Add authentication for secure dashboards.
- Add production-ready logging and error handling.
