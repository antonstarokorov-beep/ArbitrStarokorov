from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.event_repository import EventRepository
from app.schemas import BotEventIn, CRMDealEventIn
from app.services.lead_linker import LeadLinkerService

router = APIRouter(tags=["events"])


@router.post("/bot/events", status_code=status.HTTP_202_ACCEPTED)
def ingest_bot_event(payload: BotEventIn, db: Session = Depends(get_db)) -> dict[str, str]:
    lead = LeadLinkerService(db).resolve_for_bot_event(payload)
    EventRepository(db).add_bot_event(lead, payload)
    return {"status": "accepted"}


@router.post("/crm/events", status_code=status.HTTP_202_ACCEPTED)
def ingest_crm_event(payload: CRMDealEventIn, db: Session = Depends(get_db)) -> dict[str, str]:
    lead = LeadLinkerService(db).resolve_for_crm_event(payload)
    EventRepository(db).add_crm_event(lead, payload)
    return {"status": "accepted"}
