from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"   # converted to sale
    expired = "expired"
    cancelled = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    plot_id: Mapped[int] = mapped_column(ForeignKey("plots.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    area_booked_guntas: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    token_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), default=BookingStatus.pending, index=True
    )
    booked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column()

    plot: Mapped["Plot"] = relationship(back_populates="bookings")
    customer: Mapped["Customer"] = relationship(back_populates="bookings")
    agent: Mapped["User"] = relationship(back_populates="bookings")
    sale: Mapped["Sale | None"] = relationship(back_populates="booking", uselist=False)
