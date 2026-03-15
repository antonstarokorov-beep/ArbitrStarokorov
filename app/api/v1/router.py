from fastapi import APIRouter

from app.api.v1 import dashboard, dev, events, leads

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(leads.router)
api_router.include_router(events.router)
api_router.include_router(dashboard.router)
api_router.include_router(dev.router)
