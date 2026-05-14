# Plot Booking & Sales Management API

FastAPI backend for managing real-estate plot bookings, sales, payments, and agent performance.

## Features

- **JWT auth** with admin / agent roles
- **Plot CRUD** with status tracking (`available → partial → booked → sold`)
- **Smart partial selling** — sell any number of guntas; plot becomes `partial` until fully sold
- **Booking management** with 48-hour auto-expiry (APScheduler, every 15 min)
- **Payment tracking** with auto-timestamp on record creation
- **Agent leaderboard** (admin only) with revenue and commission rankings
- **Dashboard analytics** — plot counts, revenue, outstanding payments
- **WebSocket** real-time plot status broadcast on every state change

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # edit SECRET_KEY
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Architecture

```
app/
  models/      SQLAlchemy 2.0 ORM models
  schemas/     Pydantic v2 request/response schemas
  routers/     FastAPI routers (one per resource)
  core/        security, deps, APScheduler
  ws/          WebSocket ConnectionManager
alembic/       database migrations
```

## Data models

| Model    | Key fields |
|----------|-----------|
| User     | name, email, role (admin/agent) |
| Plot     | plot_number, total_area_guntas, remaining_area_guntas, price_per_gunta, status |
| Customer | name, phone, pan_number, aadhar_number |
| Booking  | plot, customer, agent, area_booked_guntas, expires_at (48 h) |
| Sale     | booking (optional), area_sold_guntas, total_amount, commission_amount |
| Payment  | sale, amount, mode (cash/cheque/neft/rtgs/upi), paid_at (auto) |
