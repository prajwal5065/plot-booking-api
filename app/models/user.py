from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class Role(str, enum.Enum):
    admin = "admin"
    agent = "agent"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.agent)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="agent")
    sales: Mapped[list["Sale"]] = relationship(back_populates="agent")
