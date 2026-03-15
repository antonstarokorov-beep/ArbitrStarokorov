from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.lead_repository import LeadRepository
from app.schemas import Lead, LeadCreate, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=Lead, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)) -> Lead:
    return LeadRepository(db).create(payload)


@router.get("", response_model=list[Lead])
def list_leads(db: Session = Depends(get_db)) -> list[Lead]:
    return LeadRepository(db).list()


@router.get("/{lead_id}", response_model=Lead)
def get_lead(lead_id: UUID, db: Session = Depends(get_db)) -> Lead:
    lead = LeadRepository(db).get(lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=Lead)
def patch_lead(lead_id: UUID, payload: LeadUpdate, db: Session = Depends(get_db)) -> Lead:
    repository = LeadRepository(db)
    lead = repository.get(lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return repository.update(lead, payload)
