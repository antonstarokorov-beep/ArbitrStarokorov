from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.schemas.common import LeadStatus, MatterType, SourceType


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    source: Mapped[SourceType] = mapped_column(Enum(SourceType, name="source_type"), nullable=False)
    click_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    bot_chat_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    crm_deal_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    matter_type: Mapped[MatterType] = mapped_column(
        Enum(MatterType, name="matter_type"), nullable=False, default=MatterType.unknown
    )
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="lead_status"), nullable=False, default=LeadStatus.new
    )
    ai_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_ltv: Mapped[float | None] = mapped_column(Float, nullable=True)
    revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    bot_events: Mapped[list["BotEvent"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    crm_events: Mapped[list["CRMEvent"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    touchpoints: Mapped[list["LeadTouchpoint"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
