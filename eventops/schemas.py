import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from eventops.models import EventStatus


class EventCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)


class EventResponse(BaseModel):
    id: uuid.UUID
    idempotency_key: str
    source: str
    type: str
    payload: dict[str, Any]
    status: EventStatus
    retry_count: int
    created_at: datetime
    processed_at: datetime | None
    error_reason: str | None

    model_config = {"from_attributes": True}
