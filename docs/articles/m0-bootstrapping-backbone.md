# M0 — Bootstrapping a Production-Minded Event-Driven Backend

Most backend side projects start with business logic.

This one starts with infrastructure.

EventOps is not a feature demo — it is a **career asset** designed to practice reliability fundamentals that matter in real systems:
- reproducibility
- async processing
- clear service boundaries
- future-ready observability and failure handling

This first milestone (M0) focuses on one thing:

> Can the distributed backbone run deterministically with one command?

If not, nothing else matters.

---

# 1. Objective of M0

Establish a minimal but production-minded foundation:

- API service
- Background worker
- Message broker
- Database
- One-command startup
- Health verification

No business logic yet. Just architecture discipline.

---

# 2. High-Level Architecture


Client
│
▼
┌───────────┐
│ API │ (FastAPI)
│ Ingestion │
└─────┬─────┘
│
▼
┌───────────┐
│ RabbitMQ │ (Broker)
└─────┬─────┘
│
▼
┌───────────┐
│ Worker │ (Celery)
│ Processing│
└─────┬─────┘
│
▼
┌───────────┐
│ Postgres │
│ Event DB │
└───────────┘


Two independent deployable units:
- `api` → request/response boundary
- `worker` → async background execution

This separation is intentional.

---

# 3. Why Separate API and Worker?

In production systems:

- APIs should stay responsive.
- Heavy or failure-prone tasks should not block requests.
- Retry logic should live outside request lifecycles.
- At-least-once delivery must be tolerated.

Even if this could be built synchronously, that would defeat the purpose.

This architecture prepares for:
- idempotent ingestion
- retry policies
- dead-letter handling
- LLM-based enrichment without blocking clients

---

# 4. Technology Choices (and Why)

## FastAPI (API Layer)

Chosen for:
- explicit data validation (Pydantic)
- OpenAPI generation
- modern async-first design
- low boilerplate

FastAPI is not the focus — it is the boundary.

---

## Celery (Worker)

Chosen because:
- mature ecosystem
- clear retry semantics
- works well with RabbitMQ
- interview-recognizable

Alternatives considered:
- asyncio + aio-pika (more control, more complexity)
- Dramatiq (cleaner, less common in some orgs)

Trade-off:
Celery is slightly heavier, but faster to ship for this purpose.

---

## RabbitMQ (Broker)

Chosen because:
- Natural fit for job-queue workloads
- Built-in dead-letter patterns
- Clear delivery semantics (at-least-once)
- Management UI for visibility

Alternatives considered:
- Redis (simpler, common, but less explicit routing semantics)
- Kafka (powerful streaming, but operationally heavier)

For a reliability-focused backend demo, RabbitMQ is defensible and explainable.

---

## PostgreSQL

Chosen because:
- Strong transactional guarantees
- JSONB support (for flexible payload modeling)
- Widely used in production systems

Future milestones will introduce:
- JSONB indexing
- idempotency constraints
- status transitions

---

## Docker Compose

Chosen because:
- One command to run the full stack
- Deterministic local reproducibility
- No “works on my machine” drift


docker compose -f infra/docker-compose.yml up --build


If the system cannot be bootstrapped cleanly, reliability discussions are meaningless.

---

# 5. Health Verification

A minimal `/healthz` endpoint was implemented to validate:

- API container builds correctly
- Networking between containers works
- The stack responds as expected


curl http://localhost:8000/healthz


Expected:


{"status":"ok"}


This small endpoint proves the infrastructure path works end-to-end.

---

# 6. Why Start With Infrastructure First?

Many side projects focus on:
- feature count
- UI
- AI integrations

But production systems fail because of:
- missing idempotency
- broken retry strategies
- lack of observability
- implicit coupling

By locking down the backbone first, the next milestones become composable.

---

# 7. What Comes Next (M1 Preview)

M1 introduces real backend discipline:

- `events` table with JSONB
- Unique idempotency key handling
- Versioned API (`/v1`)
- Celery task enqueue after ingestion
- Status transitions:
  - RECEIVED
  - PROCESSING
  - PROCESSED
  - FAILED

After that:
- retry + backoff
- dead-letter strategy
- tracing across API → worker
- metrics
- LLM-based failure explanation

---

# 8. Key Takeaways From M0

- Architecture before features.
- Separation of concerns from day one.
- Reproducibility is a reliability requirement.
- Small milestones compound.

This is not a product yet.

It is a foundation engineered to survive the next layers.

---

# Repository

Full code and roadmap:
(Insert your repo link here)

---

If you’ve built distributed systems before:

What is one reliability decision you wish you had implemented earlier?