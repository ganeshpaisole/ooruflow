"""
Ride pooling: join an existing POOL ride as a co-passenger.

Flow:
  1. Rider A books a POOL ride → becomes the "owner"
  2. Rider B calls POST /pool/{ride_id}/join → added as RidePassenger
  3. Fare is recalculated and split equally (65% × solo_fare ÷ num_passengers)
  4. Max 4 passengers per POOL ride
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, auth
from ..database import get_db
from ..fare import calculate_fare, calculate_distance_km
from ..models import User, RideType, RideStatus, RidePassenger, ScheduledRide

router = APIRouter(prefix="/pool", tags=["ride pooling"])

MAX_POOL_PASSENGERS = 4


@router.get("/available", response_model=list[schemas.ScheduledRideResponse])
async def list_available_pool_rides(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """List open POOL rides that still have seats available."""
    result = await db.execute(
        select(ScheduledRide).where(
            ScheduledRide.ride_type == RideType.POOL,
            ScheduledRide.status == RideStatus.PENDING,
            ScheduledRide.user_id != current_user.id,
        )
    )
    rides = result.scalars().all()

    available = []
    for ride in rides:
        count_result = await db.execute(
            select(func.count()).where(RidePassenger.ride_id == ride.id)
        )
        passenger_count = count_result.scalar() + 1  # +1 for owner
        if passenger_count < MAX_POOL_PASSENGERS:
            available.append(ride)

    return available


@router.post("/{ride_id}/join", status_code=201)
async def join_pool_ride(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Join an existing POOL ride as a co-passenger.
    Fare is recalculated and shared across all passengers.
    """
    ride = await crud.get_ride_by_id(db, ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    if ride.ride_type != RideType.POOL:
        raise HTTPException(status_code=400, detail="This is not a POOL ride.")
    if ride.status != RideStatus.PENDING:
        raise HTTPException(status_code=400, detail="This ride is no longer open for joining.")
    if ride.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot join your own ride.")

    # Check if already joined
    existing = await db.execute(
        select(RidePassenger).where(
            RidePassenger.ride_id == ride_id,
            RidePassenger.user_id == current_user.id,
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="You have already joined this ride.")

    # Check capacity
    count_result = await db.execute(
        select(func.count()).where(RidePassenger.ride_id == ride_id)
    )
    current_passengers = count_result.scalar() + 1  # +1 for owner
    if current_passengers >= MAX_POOL_PASSENGERS:
        raise HTTPException(status_code=400, detail="This ride is full.")

    # Add passenger
    passenger = RidePassenger(
        ride_id=ride_id,
        user_id=current_user.id,
        pickup_location=ride.pickup_location,
        dropoff_location=ride.dropoff_location,
    )
    db.add(passenger)

    # Recalculate fare split
    num_passengers = current_passengers + 1  # including new joiner
    if all([ride.pickup_lat, ride.pickup_lng, ride.dropoff_lat, ride.dropoff_lng]):
        dist = calculate_distance_km(
            ride.pickup_lat, ride.pickup_lng,
            ride.dropoff_lat, ride.dropoff_lng,
        )
        per_person_fare = calculate_fare(dist, RideType.POOL, ride.slot_start, num_passengers)
        ride.fare = per_person_fare

        # Update existing passengers' fare_share
        existing_passengers = await db.execute(
            select(RidePassenger).where(RidePassenger.ride_id == ride_id)
        )
        for p in existing_passengers.scalars().all():
            p.fare_share = per_person_fare
        passenger.fare_share = per_person_fare

    await db.commit()

    return {
        "message": f"Joined pool ride #{ride_id} successfully.",
        "passengers": num_passengers,
        "fare_per_person": ride.fare,
    }


@router.get("/{ride_id}/passengers")
async def get_pool_passengers(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Get all passengers in a pool ride."""
    ride = await crud.get_ride_by_id(db, ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    result = await db.execute(
        select(RidePassenger).where(RidePassenger.ride_id == ride_id)
    )
    passengers = result.scalars().all()
    return {"owner_user_id": ride.user_id, "co_passengers": len(passengers), "total": len(passengers) + 1}
