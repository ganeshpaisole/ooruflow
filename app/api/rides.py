from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from .. import crud, schemas, auth
from ..database import get_db
from ..models import User, RideType
from ..fare import calculate_fare, calculate_distance_km, is_peak_hour
from datetime import datetime
import pytz

router = APIRouter(prefix="/rides", tags=["rides"])


@router.post("/", response_model=schemas.ScheduledRideResponse, status_code=201)
async def book_ride(
    ride: schemas.ScheduledRideCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Book a ride. Cutoff: 8 PM IST the day before. Supports SOLO and POOL."""
    db_ride = await crud.create_ride(db=db, ride=ride, user_id=current_user.id)
    if db_ride is None:
        raise HTTPException(
            status_code=400,
            detail="Booking window closed! Rides must be scheduled before 8 PM IST the day before.",
        )
    return db_ride


@router.get("/estimate")
async def estimate_fare(
    pickup_lat: float,
    pickup_lng: float,
    dropoff_lat: float,
    dropoff_lng: float,
    ride_type: RideType = RideType.SOLO,
    slot_start: Optional[datetime] = None,
    current_user: User = Depends(auth.get_current_user),
):
    """
    Get a fare estimate before booking.
    Pass slot_start in ISO format (e.g. 2026-04-27T09:00:00+05:30).
    If omitted, uses current time (useful for checking surge status).
    """
    ist = pytz.timezone('Asia/Kolkata')
    ride_time = slot_start or datetime.now(ist)

    dist = calculate_distance_km(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
    solo_fare = calculate_fare(dist, RideType.SOLO, ride_time)
    pool_fare = calculate_fare(dist, RideType.POOL, ride_time, num_passengers=2)
    surge_active = is_peak_hour(ride_time)

    return {
        "distance_km": round(dist, 2),
        "solo_fare_inr": solo_fare,
        "pool_fare_per_person_inr": pool_fare,
        "surge_active": surge_active,
        "surge_multiplier": 1.5 if surge_active else 1.0,
    }


@router.get("/", response_model=list[schemas.ScheduledRideResponse])
async def get_my_rides(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """All scheduled rides for the authenticated user."""
    return await crud.get_user_rides(db=db, user_id=current_user.id)


@router.get("/{ride_id}", response_model=schemas.ScheduledRideResponse)
async def get_ride(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    ride = await crud.get_ride_by_id(db, ride_id)
    if not ride or ride.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Ride not found.")
    return ride


@router.delete("/{ride_id}", status_code=204)
async def cancel_ride(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Cancel a ride. Full refund if cancelled before 7 PM IST the day before."""
    result = await crud.cancel_ride(db, ride_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Ride not found or already completed/cancelled.")
