from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ws.manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/plots")
async def plot_updates(ws: WebSocket):
    """
    Real-time plot status stream.
    Clients receive JSON messages: {"event": "plot_status_changed", "data": {...}}
    No auth required on the socket — use for read-only dashboards.
    """
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keep connection alive; server pushes events
    except WebSocketDisconnect:
        manager.disconnect(ws)
