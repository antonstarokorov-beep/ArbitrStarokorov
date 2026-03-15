from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.lead_repository import LeadRepository
from app.schemas import LeadCreate, SourceType

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/seed")
def seed(db: Session = Depends(get_db)) -> dict[str, int]:
    repository = LeadRepository(db)
    fixtures = [
        LeadCreate(source=SourceType.yandex_direct, click_id="yd-001", estimated_ltv=120000),
        LeadCreate(source=SourceType.vk_ads, click_id="vk-001", estimated_ltv=90000),
        LeadCreate(source=SourceType.seo, click_id="seo-001", estimated_ltv=150000),
    ]
    for fixture in fixtures:
        repository.create(fixture)
    return {"seeded": len(fixtures)}
