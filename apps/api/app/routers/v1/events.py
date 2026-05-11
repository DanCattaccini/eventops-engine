import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from eventops.db import get_db
from eventops.models import Event, EventStatus
from eventops.schemas import EventCreate, EventResponse
from eventops.tasks import process_event

router = APIRouter(prefix="/v1/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=201)
def ingest_event(
    body: EventCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    existing = db.query(Event).filter(Event.idempotency_key == idempotency_key).first()
    if existing:
        return existing

    event = Event(
        id=uuid.uuid4(),
        idempotency_key=idempotency_key,
        source=body.source,
        type=body.type,
        payload=body.payload,
        status=EventStatus.RECEIVED,
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return db.query(Event).filter(Event.idempotency_key == idempotency_key).first()
    db.refresh(event)

    process_event.delay(str(event.id))
    return event


@router.post("/{event_id}/replay", response_model=EventResponse)
def replay_event(event_id: uuid.UUID, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status not in (EventStatus.DEAD, EventStatus.FAILED):
        raise HTTPException(
            status_code=409,
            detail=f"Only DEAD or FAILED events can be replayed (current status: {event.status})",
        )

    event.status = EventStatus.RECEIVED
    event.retry_count = 0
    event.error_reason = None
    event.processed_at = None
    db.commit()
    db.refresh(event)

    process_event.delay(str(event.id))
    return event


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: uuid.UUID, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("", response_model=list[EventResponse])
def list_events(
    status: EventStatus | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Event)
    if status is not None:
        q = q.filter(Event.status == status)
    return q.order_by(Event.created_at.desc()).limit(limit).all()
