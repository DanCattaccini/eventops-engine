"""create events table

Revision ID: 0001
Revises:
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE eventstatus AS ENUM ('RECEIVED', 'PROCESSING', 'PROCESSED', 'FAILED')")

    op.create_table(
        "events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("type", sa.String(255), nullable=False),
        sa.Column("payload", JSONB, nullable=False),
        sa.Column(
            "status",
            sa.Enum("RECEIVED", "PROCESSING", "PROCESSED", "FAILED", name="eventstatus", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_reason", sa.Text, nullable=True),
    )

    op.create_index("ix_events_idempotency_key", "events", ["idempotency_key"], unique=True)
    op.create_index("ix_events_status", "events", ["status"])
    op.create_index("ix_events_created_at", "events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_events_created_at", "events")
    op.drop_index("ix_events_status", "events")
    op.drop_index("ix_events_idempotency_key", "events")
    op.drop_table("events")
    op.execute("DROP TYPE eventstatus")
