from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.database import get_db
from app.models.sale import Sale
from app.models.user import Role, User

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/")
def leaderboard(
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role(Role.admin)),
):
    """Agent ranking by total sales revenue (admin only)."""
    q = (
        db.query(
            Sale.agent_id,
            User.name.label("agent_name"),
            func.count(Sale.id).label("total_deals"),
            func.sum(Sale.area_sold_guntas).label("total_guntas_sold"),
            func.sum(Sale.total_amount).label("total_revenue"),
            func.sum(Sale.commission_amount).label("total_commission"),
        )
        .join(User, Sale.agent_id == User.id)
        .group_by(Sale.agent_id, User.name)
    )
    if from_date:
        q = q.filter(Sale.sold_at >= from_date)
    if to_date:
        q = q.filter(Sale.sold_at <= to_date)

    rows = q.order_by(func.sum(Sale.total_amount).desc()).all()
    return [
        {
            "rank": idx + 1,
            "agent_id": r.agent_id,
            "agent_name": r.agent_name,
            "total_deals": r.total_deals,
            "total_guntas_sold": float(r.total_guntas_sold or 0),
            "total_revenue": float(r.total_revenue or 0),
            "total_commission": float(r.total_commission or 0),
        }
        for idx, r in enumerate(rows)
    ]
