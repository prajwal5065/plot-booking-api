from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int | None] = mapped_column(ForeignKey("bookings.id"))
    plot_id: Mapped[int] = mapped_column(ForeignKey("plots.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    area_sold_guntas: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    price_per_gunta: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    sold_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    booking: Mapped["Booking | None"] = relationship(back_populates="sale")
    plot: Mapped["Plot"] = relationship(back_populates="sales")
    customer: Mapped["Customer"] = relationship(back_populates="sales")
    agent: Mapped["User"] = relationship(back_populates="sales")
    payments: Mapped[list["Payment"]] = relationship(back_populates="sale")
