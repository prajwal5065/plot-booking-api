from datetime import datetime
from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: str | None = None
    address: str | None = None
    pan_number: str | None = None
    aadhar_number: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    pan_number: str | None = None
    aadhar_number: str | None = None


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None
    address: str | None
    pan_number: str | None
    aadhar_number: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
