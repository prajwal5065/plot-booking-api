from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, model_validator
from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    plot_id: int
    customer_id: int
    area_booked_guntas: Decimal
    token_amount: Decimal = Decimal("0")
    notes: str | None = None

    @model_validator(mode="after")
    def validate_area(self):
        if self.area_booked_guntas <= 0:
            raise ValueError("area_booked_guntas must be positive")
        return self


class BookingOut(BaseModel):
    id: int
    plot_id: int
    customer_id: int
    agent_id: int
    area_booked_guntas: Decimal
    token_amount: Decimal
    status: BookingStatus
    booked_at: datetime
    expires_at: datetime
    notes: str | None

    model_config = {"from_attributes": True}


class BookingConfirm(BaseModel):
    """Convert a booking to a sale — optionally override price per gunta."""
    price_per_gunta: Decimal | None = None
