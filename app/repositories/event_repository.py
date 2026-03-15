from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import BotEvent, CRMEvent, Lead, LeadTouchpoint
from app.schemas.common import LeadStatus
from app.schemas.events import BotEventIn, CRMDealEventIn


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_bot_event(self, lead: Lead, payload: BotEventIn) -> BotEvent:
        event = BotEvent(
            lead_id=lead.id,
            bot_chat_id=payload.bot_chat_id,
            matter_type=payload.matter_type.value if payload.matter_type else None,
            ai_score=payload.ai_score,
            event_type=payload.event_type,
            timestamp=payload.timestamp or datetime.now(UTC),
        )
        self.db.add(event)

        lead.bot_chat_id = payload.bot_chat_id
        if payload.matter_type:
            lead.matter_type = payload.matter_type
        if payload.ai_score is not None:
            lead.ai_score = payload.ai_score
        lead.status = LeadStatus.bot_qualified

        touchpoint = LeadTouchpoint(
            lead_id=lead.id,
            source=lead.source.value,
            click_id=lead.click_id,
            bot_chat_id=payload.bot_chat_id,
            crm_deal_id=lead.crm_deal_id,
        )
        self.db.add(touchpoint)

        self.db.add(lead)
        self.db.commit()
        self.db.refresh(event)
        return event

    def add_crm_event(self, lead: Lead, payload: CRMDealEventIn) -> CRMEvent:
        event = CRMEvent(
            lead_id=lead.id,
            crm_deal_id=payload.crm_deal_id,
            status=payload.status.value,
            revenue=payload.revenue,
            estimated_ltv=payload.estimated_ltv,
            event_type=payload.event_type,
            timestamp=payload.timestamp or datetime.now(UTC),
        )
        self.db.add(event)

        lead.crm_deal_id = payload.crm_deal_id
        lead.status = payload.status
        lead.revenue = payload.revenue
        if payload.estimated_ltv is not None:
            lead.estimated_ltv = payload.estimated_ltv

        touchpoint = LeadTouchpoint(
            lead_id=lead.id,
            source=lead.source.value,
            click_id=lead.click_id,
            bot_chat_id=lead.bot_chat_id,
            crm_deal_id=payload.crm_deal_id,
        )
        self.db.add(touchpoint)

        self.db.add(lead)
        self.db.commit()
        self.db.refresh(event)
        return event
