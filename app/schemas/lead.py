from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import LeadStatus, MatterType, SourceType


class LeadBase(BaseModel):
    source: SourceType
    click_id: str | None = None
    bot_chat_id: str | None = None
    crm_deal_id: str | None = None
    matter_type: MatterType = MatterType.unknown
    status: LeadStatus = LeadStatus.new
    ai_score: float | None = Field(default=None, ge=0.0, le=1.0)
    estimated_ltv: float | None = Field(default=None, ge=0.0)
    revenue: float = Field(default=0.0, ge=0.0)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    click_id: str | None = None
    bot_chat_id: str | None = None
    crm_deal_id: str | None = None
    matter_type: MatterType | None = None
    status: LeadStatus | None = None
    ai_score: float | None = Field(default=None, ge=0.0, le=1.0)
    estimated_ltv: float | None = Field(default=None, ge=0.0)
    revenue: float | None = Field(default=None, ge=0.0)


class Lead(LeadBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
