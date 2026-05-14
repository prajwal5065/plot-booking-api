from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.plot import Plot, PlotStatus

scheduler = BackgroundScheduler()


def expire_stale_bookings():
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        stale = (
            db.query(Booking)
            .filter(Booking.status == BookingStatus.pending, Booking.expires_at <= now)
            .all()
        )
        for booking in stale:
            booking.status = BookingStatus.expired
            plot: Plot = booking.plot
            # Release the reserved area back to the plot
            plot.remaining_area_guntas += booking.area_booked_guntas
            if plot.remaining_area_guntas >= plot.total_area_guntas:
                plot.status = PlotStatus.available
            elif plot.remaining_area_guntas > 0:
                plot.status = PlotStatus.partial
        if stale:
            db.commit()
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(expire_stale_bookings, "interval", minutes=15, id="expire_bookings")
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()
