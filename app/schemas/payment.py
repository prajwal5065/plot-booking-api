from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.payment import PaymentMode


class PaymentCreate(BaseModel):
    sale_id: int
    amount: Decimal
    mode: PaymentMode
    reference_number: str | None = None
    notes: str | None = None


class PaymentOut(BaseModel):
    id: int
    sale_id: int
    amount: Decimal
    mode: PaymentMode
    reference_number: str | None
    paid_at: datetime
    notes: str | None

    model_config = {"from_attributes": True}
