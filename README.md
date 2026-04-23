# HNG DevOps Stage 2 — Containerized Microservices

A production-ready containerized job processing system with a full CI/CD pipeline.

## Architecture

```
Internet → Nginx → Frontend (Node.js :3000)
                 → API (Python/FastAPI :8000) → Redis
                                Worker (Python) → Redis
```

## Services

| Service | Language | Port | Description |
|---------|----------|------|-------------|
| frontend | Node.js | 3000 | Job submission UI |
| api | Python/FastAPI | 8000 | REST API |
| worker | Python | — | Job processor |
| redis | Redis 7 | internal only | Job queue |

## Prerequisites

- Docker 24+
- Docker Compose v2+
- Git

## Running Locally from Scratch

```bash
# 1. Clone the repo
git clone https://github.com/Collinsthegreat/hng14-stage2-devops.git
cd hng14-stage2-devops

# 2. Create your .env
cp .env.example .env

# 3. Build and start all services
docker compose up --build

# 4. Verify all services are healthy
docker compose ps
```

A successful startup shows all 4 services with status `healthy`.

## API Endpoints

| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/` | `{"message": "API is running"}` |
| GET | `/health` | `{"message": "healthy"}` |
| POST | `/jobs` | `{"job_id": "<uuid>"}` |
| GET | `/jobs/:id` | `{"status": "pending\|processing\|completed"}` |

## CI/CD Pipeline

Stages run in strict order: `lint → test → build → security scan → integration test → deploy`

- Deploy stage runs on `main` branch pushes only
- Rolling deploy with 60s health check window per service
- Pipeline fails on any CRITICAL Trivy finding

## Live URL

**https://doflamingo.mooo.com**

## Bugs Fixed

See [FIXES.md](./FIXES.md) for a complete list of all bugs found and fixed.
