FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

COPY apps/worker /app/apps/worker

CMD ["poetry", "run", "celery", "-A", "apps.worker.worker:celery_app", "worker", "--loglevel=INFO"]
