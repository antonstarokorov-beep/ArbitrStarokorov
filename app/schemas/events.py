from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import LeadStatus, MatterType


class BotEventIn(BaseModel):
    lead_id: UUID | None = None
    click_id: str | None = None
    bot_chat_id: str
    matter_type: MatterType | None = None
    ai_score: float | None = Field(default=None, ge=0.0, le=1.0)
    event_type: str = "qualification"
    timestamp: datetime | None = None


class CRMDealEventIn(BaseModel):
    lead_id: UUID | None = None
    click_id: str | None = None
    crm_deal_id: str
    status: LeadStatus
    revenue: float = Field(default=0.0, ge=0.0)
    estimated_ltv: float | None = Field(default=None, ge=0.0)
    event_type: str = "status_update"
    timestamp: datetime | None = None
