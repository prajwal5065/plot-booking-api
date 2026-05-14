from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, Enum, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class PlotStatus(str, enum.Enum):
    available = "available"
    partial = "partial"      # some guntas sold, more remain
    booked = "booked"        # fully held under a pending booking
    sold = "sold"            # fully sold


class Plot(Base):
    __tablename__ = "plots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plot_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    survey_number: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(300))
    total_area_guntas: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    remaining_area_guntas: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    price_per_gunta: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    status: Mapped[PlotStatus] = mapped_column(Enum(PlotStatus), default=PlotStatus.available, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="plot")
    sales: Mapped[list["Sale"]] = relationship(back_populates="plot")
