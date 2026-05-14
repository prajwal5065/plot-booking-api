from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class SaleOut(BaseModel):
    id: int
    booking_id: int | None
    plot_id: int
    customer_id: int
    agent_id: int
    area_sold_guntas: Decimal
    price_per_gunta: Decimal
    total_amount: Decimal
    commission_amount: Decimal
    sold_at: datetime

    model_config = {"from_attributes": True}
