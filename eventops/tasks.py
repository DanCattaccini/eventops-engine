import os
from datetime import datetime, timezone

from celery import Celery

from eventops.db import SessionLocal
from eventops.models import Event, EventStatus

BROKER_URL = os.environ["CELERY_BROKER_URL"]

celery_app = Celery("eventops", broker=BROKER_URL)


@celery_app.task(name="eventops.process_event", bind=True)
def process_event(self, event_id: str) -> None:
    db = SessionLocal()
    try:
        event = db.get(Event, event_id)
        if event is None:
            return

        event.status = EventStatus.PROCESSING
        db.commit()

        # Processing logic will grow here (M2: retries, M5: LLM enrichment)
        event.status = EventStatus.PROCESSED
        event.processed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:
        db.rollback()
        event = db.get(Event, event_id)
        if event is not None:
            event.status = EventStatus.FAILED
            event.error_reason = str(exc)
            db.commit()
        raise exc
    finally:
        db.close()
