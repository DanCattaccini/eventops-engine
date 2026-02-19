# EventOps Roadmap

This roadmap is designed to build a **production-minded backend** incrementally, with clear “done” criteria per milestone.

Principles:
- Deliver in small slices
- Keep infra minimal until it’s justified
- Prefer decisions that are explainable in interviews
- Document trade-offs (ADRs) as you go

---

## Milestone M0 — System boot (DONE)
Goal: run a minimal distributed backbone locally.

Deliverables:
- [x] FastAPI service running in Docker
- [x] Celery worker running in Docker
- [x] RabbitMQ broker + management UI
- [x] Postgres running with persistent volume
- [x] `/healthz` endpoint
- [x] One-command startup with Docker Compose

Definition of done:
- `docker compose ps` shows all services Up
- `curl localhost:8000/healthz` returns `{"status":"ok"}`

---

## Milestone M1 — Data model + ingestion reliability
Goal: ingest events safely and enqueue processing jobs.

Deliverables:
- [ ] Postgres schema `events`:
  - `id` (UUID)
  - `idempotency_key` (string, unique)
  - `source` (string)
  - `type` (string)
  - `payload` (JSONB)
  - `status` (enum/string)
  - `created_at`, `processed_at`
  - `error_reason` (text nullable)
- [ ] Indexes:
  - BTREE on `status`, `created_at`
  - (optional) GIN on `payload` when queries justify it
- [ ] Alembic migrations
- [ ] API versioning:
  - `POST /v1/events` (accepts payload + headers)
  - `GET /v1/events/{id}`
  - `GET /v1/events?status=...`
- [ ] Idempotency:
  - Use `Idempotency-Key` header
  - If key exists, return the existing event (no duplicate inserts)
- [ ] Enqueue:
  - After insert, enqueue Celery job `process_event(event_id)`

Definition of done:
- Posting the same `Idempotency-Key` twice does not create duplicates
- Enqueued job updates status from RECEIVED → PROCESSING → PROCESSED/FAILED

---

## Milestone M2 — Failure handling (retries + DLQ)
Goal: handle real failure modes without manual babysitting.

Deliverables:
- [ ] Retry policy:
  - exponential backoff with cap
  - max retries (e.g., 5)
- [ ] Dead-letter strategy:
  - “DEAD” state (logical DLQ) AND/OR Rabbit DLQ queue
- [ ] Replay mechanism:
  - `POST /v1/events/{id}/replay` (admin-only later)
- [ ] Clear status transitions + timestamps
- [ ] Idempotent processing:
  - worker safe under at-least-once delivery

Definition of done:
- Simulated failure triggers retries and ends in DEAD after max retries
- Replay re-enqueues and reprocesses successfully

---

## Milestone M3 — Observability (logs, traces, metrics)
Goal: debug issues like a production engineer.

Deliverables:
- [ ] Structured logs (JSON) with correlation id
- [ ] OpenTelemetry tracing across API → worker
- [ ] Tracing UI (Jaeger) OR Grafana Tempo (later)
- [ ] Metrics:
  - request latency histogram
  - processed events counter
  - failures/retries counters
- [ ] Basic dashboards

Definition of done:
- You can trace a single event across API + worker
- You can see retry rate and failure reasons

---

## Milestone M4 — Auth + RBAC
Goal: introduce real access control for production realism.

Deliverables:
- [ ] Auth strategy (JWT/OAuth2)
- [ ] RBAC roles (admin/operator/viewer)
- [ ] Secure endpoints (ingest, query, replay)
- [ ] Secrets management for local/dev

Definition of done:
- Non-auth users cannot ingest/query
- Replay is restricted

---

## Milestone M5 — LLM enrichment (applied, not hype)
Goal: use LLM only where it improves outcomes.

Deliverables:
- [ ] Provider interface (`LLMClient`)
- [ ] OpenAI primary + Gemini fallback
- [ ] Enrichment only on failure path:
  - summarize failure
  - probable cause
  - suggested remediation steps
- [ ] Store enrichment output in DB (separate field/table)

Definition of done:
- A failed event gets an explanation and recommended action stored
- Fallback works when primary provider fails

---

## Milestone M6 — Similarity search (optional)
Goal: find “similar incidents” fast.

Deliverables:
- [ ] pgvector in Postgres
- [ ] embeddings for error summaries
- [ ] `GET /v1/events/{id}/similar`

Definition of done:
- Similar failures are retrievable with reasonable relevance

---

## Milestone M7 — AWS deployment (pragmatic)
Goal: deploy with minimal friction, then iterate.

Deliverables:
- [ ] RDS Postgres
- [ ] EC2 + docker compose (API + worker + RabbitMQ) OR ECS later
- [ ] basic logging (CloudWatch) OR OTel exporter
- [ ] deployment guide in docs

Definition of done:
- A fresh AWS environment can run the system end-to-end
- You can demo ingestion + processing remotely

---

## Suggested ADRs to write (as you reach them)
- ADR: RabbitMQ + Celery vs Redis vs Kafka
- ADR: SQLAlchemy + Alembic vs alternatives
- ADR: JSONB + indexes strategy
- ADR: retry/DLQ policy
- ADR: OTel + Jaeger vs Tempo/Loki
- ADR: LLM provider strategy + fallback
- ADR: pgvector vs external vector DB