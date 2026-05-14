from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.database import get_db
from app.models.plot import Plot, PlotStatus
from app.models.user import Role, User
from app.schemas.plot import PlotCreate, PlotOut, PlotUpdate
from app.ws.manager import manager

router = APIRouter(prefix="/plots", tags=["plots"])


@router.post("/", response_model=PlotOut, status_code=status.HTTP_201_CREATED)
async def create_plot(payload: PlotCreate, db: Session = Depends(get_db),
                      _admin: User = Depends(require_role(Role.admin))):
    if db.query(Plot).filter(Plot.plot_number == payload.plot_number).first():
        raise HTTPException(status_code=400, detail="Plot number already exists")
    plot = Plot(
        **payload.model_dump(),
        remaining_area_guntas=payload.total_area_guntas,
    )
    db.add(plot)
    db.commit()
    db.refresh(plot)
    await manager.broadcast("plot_created", {"plot_id": plot.id, "status": plot.status})
    return plot


@router.get("/", response_model=list[PlotOut])
def list_plots(status: PlotStatus | None = None, db: Session = Depends(get_db),
               _user: User = Depends(get_current_user)):
    q = db.query(Plot)
    if status:
        q = q.filter(Plot.status == status)
    return q.all()


@router.get("/{plot_id}", response_model=PlotOut)
def get_plot(plot_id: int, db: Session = Depends(get_db),
             _user: User = Depends(get_current_user)):
    plot = db.get(Plot, plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    return plot


@router.patch("/{plot_id}", response_model=PlotOut)
async def update_plot(plot_id: int, payload: PlotUpdate, db: Session = Depends(get_db),
                      _admin: User = Depends(require_role(Role.admin))):
    plot = db.get(Plot, plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(plot, field, value)
    db.commit()
    db.refresh(plot)
    await manager.broadcast("plot_updated", {"plot_id": plot.id, "status": plot.status})
    return plot


@router.delete("/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plot(plot_id: int, db: Session = Depends(get_db),
                      _admin: User = Depends(require_role(Role.admin))):
    plot = db.get(Plot, plot_id)
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    if plot.status != PlotStatus.available:
        raise HTTPException(status_code=400, detail="Cannot delete a plot that has bookings or sales")
    db.delete(plot)
    db.commit()
    await manager.broadcast("plot_deleted", {"plot_id": plot_id})
