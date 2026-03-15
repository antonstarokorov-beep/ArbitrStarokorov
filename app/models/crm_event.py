from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CRMEvent(Base):
    __tablename__ = "crm_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    crm_deal_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_ltv: Mapped[float | None] = mapped_column(Float, nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, default="status_update")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    lead = relationship("Lead", back_populates="crm_events")
