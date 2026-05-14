from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment
from app.models.plot import Plot, PlotStatus
from app.models.sale import Sale
from app.models.user import Role, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(_admin: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)):
    plot_counts = {
        row.status: row.cnt
        for row in db.query(Plot.status, func.count(Plot.id).label("cnt")).group_by(Plot.status).all()
    }
    total_revenue = db.query(func.sum(Sale.total_amount)).scalar() or 0
    total_commission = db.query(func.sum(Sale.commission_amount)).scalar() or 0
    total_collected = db.query(func.sum(Payment.amount)).scalar() or 0
    pending_bookings = db.query(func.count(Booking.id)).filter(
        Booking.status == BookingStatus.pending
    ).scalar() or 0

    return {
        "plots": {
            "available": plot_counts.get(PlotStatus.available, 0),
            "partial": plot_counts.get(PlotStatus.partial, 0),
            "booked": plot_counts.get(PlotStatus.booked, 0),
            "sold": plot_counts.get(PlotStatus.sold, 0),
        },
        "sales": {
            "total_revenue": float(total_revenue),
            "total_commission": float(total_commission),
            "total_collected": float(total_collected),
            "outstanding": float(total_revenue - total_collected),
        },
        "bookings": {
            "pending": pending_bookings,
        },
    }
