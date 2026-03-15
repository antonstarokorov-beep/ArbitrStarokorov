from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: LeadCreate) -> Lead:
        lead = Lead(**payload.model_dump())
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def list(self) -> list[Lead]:
        return list(self.db.scalars(select(Lead).order_by(Lead.created_at.desc())))

    def get(self, lead_id: UUID) -> Lead | None:
        return self.db.get(Lead, lead_id)

    def find_by_click_id(self, click_id: str) -> Lead | None:
        return self.db.scalar(select(Lead).where(Lead.click_id == click_id))

    def update(self, lead: Lead, payload: LeadUpdate) -> Lead:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
