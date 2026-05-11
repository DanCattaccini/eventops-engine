# ADR-0002 — Retry and Dead-Letter Strategy

**Status:** Accepted
**Date:** 2026-05-11

## Context

Event processing can fail transiently (network blip, downstream timeout) or permanently (malformed payload, bug). We need a policy that:

- Retries transient failures automatically without manual intervention
- Stops retrying eventually and surfaces events that are permanently broken
- Allows operators to re-enqueue fixed events without data loss

## Decision

### Retry policy (Celery)
- Max 5 retries (`max_retries=5`)
- Exponential backoff: `countdown = 2^attempt` seconds → 1 s, 2 s, 4 s, 8 s, 16 s
- Total worst-case retry window: ~31 s before an event is declared DEAD

### Dead-letter strategy: logical DLQ via `DEAD` status
Events that exhaust all retries transition to `DEAD` in the `events` table.

**Why not a RabbitMQ DLX/DLQ queue?**
A Rabbit DLQ is opaque — events sit in a queue with no rich metadata. Using a `DEAD` status in Postgres means:
- Operators can query dead events by source, type, error, time range
- Dead events are visible in the same `GET /v1/events?status=DEAD` API
- Replay is a simple API call (`POST /v1/events/{id}/replay`) that resets the event and re-enqueues

A Rabbit DLX could be layered on top later for routing alerts, but it adds no observability value that the DB status doesn't already provide.

### Replay
`POST /v1/events/{id}/replay` accepts only `DEAD` or `FAILED` events, resets `status→RECEIVED`, clears `retry_count` and `error_reason`, then re-enqueues. The full retry budget is restored.

### Idempotent processing
The worker checks `event.status == PROCESSED` before doing any work. Combined with Celery's at-least-once delivery, this makes double-delivery harmless.

## Status transitions

```
RECEIVED → PROCESSING → PROCESSED
                      ↘ FAILED → (retry) → PROCESSING → ...
                                          → DEAD
DEAD/FAILED → (replay) → RECEIVED
```

## Trade-offs

| Option | Pro | Con |
|--------|-----|-----|
| Logical DLQ (chosen) | Queryable, replayable via API | Must poll DB for dead events |
| Rabbit DLX queue | Native broker feature | Opaque, harder to query/replay |
| Both | Belt-and-suspenders | Extra complexity, two sources of truth |

For the current scale a logical DLQ is sufficient. A Rabbit DLX can be added in M7 (AWS) if alerting on queue depth becomes a requirement.
