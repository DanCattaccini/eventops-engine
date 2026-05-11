import os
from datetime import datetime, timezone

from celery import Celery

from eventops.db import SessionLocal
from eventops.models import Event, EventStatus

BROKER_URL = os.environ["CELERY_BROKER_URL"]

celery_app = Celery("eventops", broker=BROKER_URL)

MAX_RETRIES = 5
# Countdown in seconds per attempt: 2, 4, 8, 16, 32 (capped)
_BACKOFF_BASE = 2


@celery_app.task(name="eventops.process_event", bind=True, max_retries=MAX_RETRIES)
def process_event(self, event_id: str) -> None:
    db = SessionLocal()
    try:
        event = db.get(Event, event_id)
        if event is None:
            return
        # At-least-once guard: skip if already successfully processed
        if event.status == EventStatus.PROCESSED:
            return

        event.status = EventStatus.PROCESSING
        db.commit()

        _do_process(event)

        event.status = EventStatus.PROCESSED
        event.processed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as exc:
        db.rollback()

        attempt = self.request.retries  # 0-based: 0 on first failure
        is_final = attempt >= MAX_RETRIES

        event = db.get(Event, event_id)
        if event is not None:
            event.retry_count = attempt + 1
            event.error_reason = str(exc)
            event.status = EventStatus.DEAD if is_final else EventStatus.FAILED
            db.commit()

        if not is_final:
            countdown = _BACKOFF_BASE ** attempt  # 1, 2, 4, 8, 16 s
            raise self.retry(exc=exc, countdown=countdown)
    finally:
        db.close()


def _do_process(event: Event) -> None:
    """Placeholder for real domain processing logic (grows in future milestones)."""
    pass
