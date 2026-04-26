"""
Real-time ride tracking via WebSocket.

Driver app connects to: WS /ws/rides/{ride_id}/driver
  → sends GPS every 5 seconds: {"lat": 12.9716, "lng": 77.5946}

Rider app connects to: WS /ws/rides/{ride_id}/track
  → receives live location updates from the driver

In-memory store is sufficient for MVP (single server).
For multi-server prod: replace with Redis Pub/Sub.
"""
import asyncio
import json
import logging
from collections import defaultdict
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, auth
from ..database import get_db

router = APIRouter(tags=["tracking"])
logger = logging.getLogger(__name__)

# ride_id → list of rider WebSocket connections
_rider_connections: Dict[int, List[WebSocket]] = defaultdict(list)
# ride_id → last known driver location
_driver_locations: Dict[int, dict] = {}


@router.websocket("/ws/rides/{ride_id}/driver")
async def driver_location_stream(
    websocket: WebSocket,
    ride_id: int,
    token: str = Query(...),
):
    """
    Driver sends GPS coordinates here every ~5 seconds.
    The server fan-outs the update to all connected riders.

    Connect with: ws://host/ws/rides/{ride_id}/driver?token=<jwt>
    Send JSON: {"lat": 12.9716, "lng": 77.5946}
    """
    # Validate JWT from query param (WebSockets can't set headers easily)
    try:
        from jose import jwt as jose_jwt
        from ..auth import SECRET_KEY, ALGORITHM
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            await websocket.close(code=4001)
            return
    except Exception:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    logger.info(f"Driver connected to ride #{ride_id} tracking stream.")

    try:
        while True:
            data = await websocket.receive_text()
            location = json.loads(data)

            if "lat" not in location or "lng" not in location:
                await websocket.send_json({"error": "Send {lat, lng}"})
                continue

            _driver_locations[ride_id] = location

            # Fan-out to all riders watching this ride
            dead = []
            for rider_ws in _rider_connections[ride_id]:
                try:
                    await rider_ws.send_json({"type": "location", **location})
                except Exception:
                    dead.append(rider_ws)
            for ws in dead:
                _rider_connections[ride_id].remove(ws)

    except WebSocketDisconnect:
        logger.info(f"Driver disconnected from ride #{ride_id}.")


@router.websocket("/ws/rides/{ride_id}/track")
async def rider_tracking_stream(
    websocket: WebSocket,
    ride_id: int,
    token: str = Query(...),
):
    """
    Rider connects here to receive live driver location.

    Connect with: ws://host/ws/rides/{ride_id}/track?token=<jwt>
    Receive JSON: {"type": "location", "lat": ..., "lng": ...}
    """
    try:
        from jose import jwt as jose_jwt
        from ..auth import SECRET_KEY, ALGORITHM
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            await websocket.close(code=4001)
            return
    except Exception:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    _rider_connections[ride_id].append(websocket)
    logger.info(f"Rider connected to ride #{ride_id} tracking stream.")

    # Send last known location immediately if available
    if ride_id in _driver_locations:
        await websocket.send_json({"type": "location", **_driver_locations[ride_id]})

    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        if websocket in _rider_connections[ride_id]:
            _rider_connections[ride_id].remove(websocket)
        logger.info(f"Rider disconnected from ride #{ride_id}.")
