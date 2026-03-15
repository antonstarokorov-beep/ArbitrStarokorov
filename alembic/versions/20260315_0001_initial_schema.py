"""initial schema

Revision ID: 20260315_0001
Revises: 
Create Date: 2026-03-15 00:00:01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260315_0001"
down_revision = None
branch_labels = None
depends_on = None


source_type = sa.Enum(
    "yandex_direct",
    "vk_ads",
    "yandex_business",
    "maps",
    "2gis",
    "seo",
    "offline",
    "referral",
    name="source_type",
)
lead_status = sa.Enum("new", "bot_qualified", "in_progress", "won", "lost", name="lead_status")
matter_type = sa.Enum(
    "arbitration",
    "bankruptcy",
    "family",
    "real_estate",
    "debt_collection",
    "corporate",
    "unknown",
    name="matter_type",
)


def upgrade() -> None:
    source_type.create(op.get_bind(), checkfirst=True)
    lead_status.create(op.get_bind(), checkfirst=True)
    matter_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("source", source_type, nullable=False),
        sa.Column("click_id", sa.String(length=255), nullable=True),
        sa.Column("bot_chat_id", sa.String(length=255), nullable=True),
        sa.Column("crm_deal_id", sa.String(length=255), nullable=True),
        sa.Column("matter_type", matter_type, nullable=False, server_default="unknown"),
        sa.Column("status", lead_status, nullable=False, server_default="new"),
        sa.Column("ai_score", sa.Float(), nullable=True),
        sa.Column("estimated_ltv", sa.Float(), nullable=True),
        sa.Column("revenue", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_leads_click_id", "leads", ["click_id"])
    op.create_index("ix_leads_bot_chat_id", "leads", ["bot_chat_id"])
    op.create_index("ix_leads_crm_deal_id", "leads", ["crm_deal_id"])

    op.create_table(
        "bot_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bot_chat_id", sa.String(length=255), nullable=False),
        sa.Column("matter_type", sa.String(length=64), nullable=True),
        sa.Column("ai_score", sa.Float(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False, server_default="qualification"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_bot_events_bot_chat_id", "bot_events", ["bot_chat_id"])

    op.create_table(
        "crm_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("crm_deal_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("revenue", sa.Float(), nullable=False, server_default="0"),
        sa.Column("estimated_ltv", sa.Float(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False, server_default="status_update"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_crm_events_crm_deal_id", "crm_events", ["crm_deal_id"])

    op.create_table(
        "lead_touchpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("click_id", sa.String(length=255), nullable=True),
        sa.Column("bot_chat_id", sa.String(length=255), nullable=True),
        sa.Column("crm_deal_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("lead_touchpoints")
    op.drop_index("ix_crm_events_crm_deal_id", table_name="crm_events")
    op.drop_table("crm_events")
    op.drop_index("ix_bot_events_bot_chat_id", table_name="bot_events")
    op.drop_table("bot_events")
    op.drop_index("ix_leads_crm_deal_id", table_name="leads")
    op.drop_index("ix_leads_bot_chat_id", table_name="leads")
    op.drop_index("ix_leads_click_id", table_name="leads")
    op.drop_table("leads")

    matter_type.drop(op.get_bind(), checkfirst=True)
    lead_status.drop(op.get_bind(), checkfirst=True)
    source_type.drop(op.get_bind(), checkfirst=True)
