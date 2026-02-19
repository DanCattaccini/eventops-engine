# ADR 0001: Choose RabbitMQ as the message broker

## Status
Accepted

## Context
We need a broker for asynchronous event processing with retries and a dead-letter strategy.
The goal is to ship a reliable MVP quickly while keeping the architecture defensible in interviews.

## Decision
Use RabbitMQ as the broker and Celery as the worker framework.

## Alternatives considered
- Redis as broker (simpler to run, common in jobs/queues)
- Kafka (powerful streaming, but higher operational complexity)

## Consequences
Positive:
- Simple setup for a job-queue workflow
- Natural DLQ semantics and routing patterns
- Widely recognized in backend interviews

Negative:
- Not a streaming log like Kafka
- Requires running an additional service locally and in deployment