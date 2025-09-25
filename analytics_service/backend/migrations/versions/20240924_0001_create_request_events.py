"""create request events table

Revision ID: 20240924_0001
Revises: 
Create Date: 2024-09-24 00:00:00.000000

"""

from __future__ import annotations


from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20240924_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "request_events",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=False),
        sa.Column("originated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("chat_id", sa.String(length=64), nullable=True),
        sa.Column("message_id", sa.BigInteger(), nullable=True),
        sa.Column("tile_id", sa.String(length=64), nullable=True),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False),
        sa.Column("status", sa.Enum("SUCCESS", "ERROR", "PARTIAL", name="request_status"), nullable=False),
        sa.Column("error_payload", sa.JSON(), nullable=True),
        sa.Column("numbers", sa.JSON(), nullable=True),
        sa.Column("raw_prompt", sa.JSON(), nullable=True),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index(op.f("ix_request_events_chat_id"), "request_events", ["chat_id"], unique=False)
    op.create_index(op.f("ix_request_events_id"), "request_events", ["id"], unique=False)
    op.create_index(op.f("ix_request_events_originated_at"), "request_events", ["originated_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_request_events_originated_at"), table_name="request_events")
    op.drop_index(op.f("ix_request_events_id"), table_name="request_events")
    op.drop_index(op.f("ix_request_events_chat_id"), table_name="request_events")
    op.drop_table("request_events")
    op.execute("DROP TYPE IF EXISTS request_status")

