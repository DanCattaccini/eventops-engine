"""add DEAD status and retry_count to events

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-11
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside a transaction block in Postgres
    conn = op.get_bind()
    conn.execution_options(isolation_level="AUTOCOMMIT").execute(
        sa.text("ALTER TYPE eventstatus ADD VALUE IF NOT EXISTS 'DEAD'")
    )

    op.add_column("events", sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("events", "retry_count")
    # Removing an enum value in Postgres requires recreating the type — not worth it for dev
