from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Lead
from app.schemas.common import LeadStatus, SourceType
from app.schemas.dashboard import ChannelMetric, DashboardSummary


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def build_summary(self) -> DashboardSummary:
        total_leads = self.db.scalar(select(func.count()).select_from(Lead)) or 0
        qualified_leads = self.db.scalar(
            select(func.count()).select_from(Lead).where(Lead.status == LeadStatus.bot_qualified)
        ) or 0
        active_leads = self.db.scalar(
            select(func.count()).select_from(Lead).where(Lead.status.in_([LeadStatus.in_progress, LeadStatus.bot_qualified]))
        ) or 0
        paid_leads = self.db.scalar(select(func.count()).select_from(Lead).where(Lead.revenue > 0)) or 0
        total_revenue = self.db.scalar(select(func.coalesce(func.sum(Lead.revenue), 0.0))) or 0.0
        avg_ai_score = self.db.scalar(select(func.avg(Lead.ai_score)))

        query = select(
            Lead.source,
            func.count(Lead.id),
            func.sum(case((Lead.status == LeadStatus.bot_qualified, 1), else_=0)),
            func.coalesce(func.sum(Lead.revenue), 0.0),
        ).group_by(Lead.source)
        rows = self.db.execute(query).all()

        by_channel = [
            ChannelMetric(
                source=SourceType(source),
                leads=leads,
                qualified=qualified,
                revenue=float(revenue),
            )
            for source, leads, qualified, revenue in rows
        ]

        return DashboardSummary(
            total_leads=total_leads,
            qualified_leads=qualified_leads,
            active_leads=active_leads,
            paid_leads=paid_leads,
            total_revenue=float(total_revenue),
            avg_ai_score=float(avg_ai_score) if avg_ai_score is not None else None,
            by_channel=by_channel,
        )
