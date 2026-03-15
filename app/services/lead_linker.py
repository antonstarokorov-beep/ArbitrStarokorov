from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Lead
from app.repositories.lead_repository import LeadRepository
from app.schemas.events import BotEventIn, CRMDealEventIn


class LeadLinkerService:
    def __init__(self, db: Session):
        self.repo = LeadRepository(db)

    def resolve_for_bot_event(self, payload: BotEventIn) -> Lead:
        if payload.lead_id:
            lead = self.repo.get(payload.lead_id)
            if lead:
                return lead
        if payload.click_id:
            lead = self.repo.find_by_click_id(payload.click_id)
            if lead:
                return lead
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found for bot event")

    def resolve_for_crm_event(self, payload: CRMDealEventIn) -> Lead:
        if payload.lead_id:
            lead = self.repo.get(payload.lead_id)
            if lead:
                return lead
        if payload.click_id:
            lead = self.repo.find_by_click_id(payload.click_id)
            if lead:
                return lead
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found for crm event")
