"""
Ratings & Reviews API.

After a ride is COMPLETED:
  - Rider can rate the driver (rated_user_id = driver's user_id)
  - Driver can rate the rider (rated_user_id = rider's user_id)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, auth
from ..database import get_db
from ..models import User, Rating, RideStatus, Driver

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("/", response_model=schemas.RatingResponse, status_code=201)
async def submit_rating(
    rating: schemas.RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Rate after a completed ride.
    The ride must be COMPLETED and the current user must be a participant.
    """
    ride = await crud.get_ride_by_id(db, rating.ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    if ride.status != RideStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only rate completed rides.")

    # Check the caller is the rider or the driver of this ride
    driver = await crud.get_driver_by_id(db, ride.driver_id) if ride.driver_id else None
    is_rider = ride.user_id == current_user.id
    is_driver = driver and driver.user_id == current_user.id
    if not is_rider and not is_driver:
        raise HTTPException(status_code=403, detail="You are not a participant of this ride.")

    # Prevent duplicate ratings
    existing = await db.execute(
        select(Rating).where(
            Rating.ride_id == rating.ride_id,
            Rating.rated_by_user_id == current_user.id,
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="You have already rated this ride.")

    db_rating = await crud.create_rating(db, rating, current_user.id)

    # Update driver's average rating if rider rated the driver
    if is_rider and driver:
        all_ratings = await db.execute(
            select(Rating).where(Rating.rated_user_id == rating.rated_user_id)
        )
        ratings_list = all_ratings.scalars().all()
        avg = sum(r.stars for r in ratings_list) / len(ratings_list)
        driver.avg_rating = round(avg, 2)
        await db.commit()

    return db_rating


@router.get("/ride/{ride_id}", response_model=list[schemas.RatingResponse])
async def get_ride_ratings(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    result = await db.execute(select(Rating).where(Rating.ride_id == ride_id))
    return result.scalars().all()
