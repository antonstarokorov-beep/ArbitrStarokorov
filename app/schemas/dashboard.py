from pydantic import BaseModel

from app.schemas.common import SourceType


class ChannelMetric(BaseModel):
    source: SourceType
    leads: int
    qualified: int
    revenue: float


class DashboardSummary(BaseModel):
    total_leads: int
    qualified_leads: int
    active_leads: int
    paid_leads: int
    total_revenue: float
    avg_ai_score: float | None
    by_channel: list[ChannelMetric]
