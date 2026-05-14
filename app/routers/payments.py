from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.payment import Payment
from app.models.sale import Sale
from app.models.user import Role, User
from app.schemas.payment import PaymentCreate, PaymentOut

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def record_payment(payload: PaymentCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    sale = db.get(Sale, payload.sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if current_user.role == Role.agent and sale.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    payment = Payment(**payload.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/sale/{sale_id}", response_model=list[PaymentOut])
def payments_for_sale(sale_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if current_user.role == Role.agent and sale.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(Payment).filter(Payment.sale_id == sale_id).all()
