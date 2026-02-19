# EventOps — Event-driven Backend + LLM Enrichment (Career Asset)

EventOps is a **career asset** project: a production-minded backend system built to practice and demonstrate reliability fundamentals (not a “pretty demo”).

The goal is to develop real-world backend confidence by implementing patterns that matter in production:
**idempotency, retries/DLQ, migrations, observability, and secure auth**, plus **LLM enrichment** where it actually adds value.

---

## Current milestone (M0)

A reproducible local stack is up and running:

- **API:** FastAPI + Uvicorn
- **Worker:** Celery
- **Broker:** RabbitMQ (management UI enabled)
- **Database:** PostgreSQL
- **Infra:** Docker Compose

Healthcheck:
- `GET /healthz`

---

## Architecture (high level)

Client → **API (FastAPI)** → persist event → **enqueue job (RabbitMQ)** → **Worker (Celery)** → process → update status in **Postgres**

Two deployable units:
- `api`: request/response boundary (ingestion + queries)
- `worker`: asynchronous processing (retries, DLQ, enrichment)

---

## Quickstart (local)

### Requirements
- Docker + Docker Compose
- Poetry (for local Python tooling)

### Run the stack
From repo root:

```bash
docker compose -f infra/docker-compose.yml up --build