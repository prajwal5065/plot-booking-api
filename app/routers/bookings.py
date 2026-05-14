from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user, require_role
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.plot import Plot, PlotStatus
from app.models.sale import Sale
from app.models.user import Role, User
from app.schemas.booking import BookingConfirm, BookingCreate, BookingOut
from app.schemas.sale import SaleOut
from app.ws.manager import manager

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _reserve_plot_area(plot: Plot, area: Decimal):
    """Deduct area from remaining and update plot status."""
    if area > plot.remaining_area_guntas:
        raise HTTPException(
            status_code=400,
            detail=f"Requested {area} guntas exceeds available {plot.remaining_area_guntas}",
        )
    plot.remaining_area_guntas -= area
    if plot.remaining_area_guntas == 0:
        plot.status = PlotStatus.booked
    else:
        plot.status = PlotStatus.partial


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(payload: BookingCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    plot = db.get(Plot, payload.plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    if plot.status == PlotStatus.sold:
        raise HTTPException(status_code=400, detail="Plot is fully sold")

    _reserve_plot_area(plot, payload.area_booked_guntas)

    booking = Booking(
        plot_id=payload.plot_id,
        customer_id=payload.customer_id,
        agent_id=current_user.id,
        area_booked_guntas=payload.area_booked_guntas,
        token_amount=payload.token_amount,
        notes=payload.notes,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.booking_expiry_hours),
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    await manager.broadcast("plot_status_changed", {"plot_id": plot.id, "status": plot.status})
    return booking


@router.get("/", response_model=list[BookingOut])
def list_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Booking)
    if current_user.role == Role.agent:
        q = q.filter(Booking.agent_id == current_user.id)
    return q.all()


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if current_user.role == Role.agent and booking.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return booking


@router.post("/{booking_id}/confirm", response_model=SaleOut)
async def confirm_booking(booking_id: int, payload: BookingConfirm,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail=f"Booking is {booking.status}, not pending")
    if current_user.role == Role.agent and booking.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    plot = booking.plot
    price_per_gunta = payload.price_per_gunta or plot.price_per_gunta
    total = booking.area_booked_guntas * price_per_gunta
    commission = total * Decimal(str(settings.commission_rate))

    sale = Sale(
        booking_id=booking.id,
        plot_id=plot.id,
        customer_id=booking.customer_id,
        agent_id=booking.agent_id,
        area_sold_guntas=booking.area_booked_guntas,
        price_per_gunta=price_per_gunta,
        total_amount=total,
        commission_amount=commission,
    )
    db.add(sale)

    booking.status = BookingStatus.confirmed

    # Smart partial selling: if remaining area is 0 mark sold, else keep partial
    if plot.remaining_area_guntas == 0:
        plot.status = PlotStatus.sold
    else:
        plot.status = PlotStatus.partial

    db.commit()
    db.refresh(sale)
    await manager.broadcast("plot_status_changed", {"plot_id": plot.id, "status": plot.status})
    return sale


@router.post("/{booking_id}/cancel", response_model=BookingOut)
async def cancel_booking(booking_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a {booking.status} booking")
    if current_user.role == Role.agent and booking.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    plot = booking.plot
    plot.remaining_area_guntas += booking.area_booked_guntas
    plot.status = PlotStatus.available if plot.remaining_area_guntas >= plot.total_area_guntas else PlotStatus.partial
    booking.status = BookingStatus.cancelled

    db.commit()
    db.refresh(booking)
    await manager.broadcast("plot_status_changed", {"plot_id": plot.id, "status": plot.status})
    return booking
