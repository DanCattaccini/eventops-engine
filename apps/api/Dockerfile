FROM python:3.13-slim

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy project metadata first (better layer caching)
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and deps
RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

# Copy source
COPY apps/api/app /app/app

EXPOSE 8000

CMD ["poetry", "run", "python", "-m", "uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
