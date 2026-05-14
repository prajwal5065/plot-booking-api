from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.scheduler import start_scheduler, stop_scheduler
from app.database import Base, engine
from app.routers import auth, bookings, customers, dashboard, leaderboard, payments, plots, sales, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Plot Booking & Sales Management API",
    description="Manage plots, bookings, sales, payments, and agent performance.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(plots.router)
app.include_router(customers.router)
app.include_router(bookings.router)
app.include_router(sales.router)
app.include_router(payments.router)
app.include_router(leaderboard.router)
app.include_router(dashboard.router)
app.include_router(ws.router)
