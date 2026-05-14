from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class PaymentMode(str, enum.Enum):
    cash = "cash"
    cheque = "cheque"
    neft = "neft"
    rtgs = "rtgs"
    upi = "upi"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    mode: Mapped[PaymentMode] = mapped_column(Enum(PaymentMode))
    reference_number: Mapped[str | None] = mapped_column(String(100))
    # auto-stamped on record creation — not editable
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    notes: Mapped[str | None] = mapped_column()

    sale: Mapped["Sale"] = relationship(back_populates="payments")
