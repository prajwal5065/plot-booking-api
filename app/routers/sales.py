from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user
from app.database import get_db
from app.models.plot import Plot, PlotStatus
from app.models.sale import Sale
from app.models.user import Role, User
from app.schemas.plot import PlotSellRequest
from app.schemas.sale import SaleOut
from app.ws.manager import manager

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("/direct", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
async def direct_sell(payload: PlotSellRequest, plot_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    """Sell part of a plot directly without a prior booking (walk-in sale)."""
    plot = db.get(Plot, plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    if plot.status == PlotStatus.sold:
        raise HTTPException(status_code=400, detail="Plot is fully sold")
    if payload.area_guntas > plot.remaining_area_guntas:
        raise HTTPException(
            status_code=400,
            detail=f"Requested {payload.area_guntas} guntas exceeds available {plot.remaining_area_guntas}",
        )

    price_per_gunta = payload.price_per_gunta or plot.price_per_gunta
    total = payload.area_guntas * price_per_gunta
    commission = total * Decimal(str(settings.commission_rate))

    sale = Sale(
        plot_id=plot.id,
        customer_id=payload.customer_id,
        agent_id=current_user.id,
        area_sold_guntas=payload.area_guntas,
        price_per_gunta=price_per_gunta,
        total_amount=total,
        commission_amount=commission,
    )
    db.add(sale)

    plot.remaining_area_guntas -= payload.area_guntas
    plot.status = PlotStatus.sold if plot.remaining_area_guntas == 0 else PlotStatus.partial

    db.commit()
    db.refresh(sale)
    await manager.broadcast("plot_status_changed", {"plot_id": plot.id, "status": plot.status})
    return sale


@router.get("/", response_model=list[SaleOut])
def list_sales(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Sale)
    if current_user.role == Role.agent:
        q = q.filter(Sale.agent_id == current_user.id)
    return q.all()


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if current_user.role == Role.agent and sale.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return sale
