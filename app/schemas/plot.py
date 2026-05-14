from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, model_validator
from app.models.plot import PlotStatus


class PlotCreate(BaseModel):
    plot_number: str
    survey_number: str
    location: str
    total_area_guntas: Decimal
    price_per_gunta: Decimal
    description: str | None = None

    @model_validator(mode="after")
    def validate_area(self):
        if self.total_area_guntas <= 0:
            raise ValueError("total_area_guntas must be positive")
        return self


class PlotUpdate(BaseModel):
    survey_number: str | None = None
    location: str | None = None
    price_per_gunta: Decimal | None = None
    description: str | None = None


class PlotOut(BaseModel):
    id: int
    plot_number: str
    survey_number: str
    location: str
    total_area_guntas: Decimal
    remaining_area_guntas: Decimal
    price_per_gunta: Decimal
    status: PlotStatus
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlotSellRequest(BaseModel):
    """Direct (no booking) partial or full sale of a plot area."""
    customer_id: int
    area_guntas: Decimal
    price_per_gunta: Decimal | None = None  # override if negotiated

    @model_validator(mode="after")
    def validate_area(self):
        if self.area_guntas <= 0:
            raise ValueError("area_guntas must be positive")
        return self
