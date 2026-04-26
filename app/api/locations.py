"""
Saved locations for quick ride booking.
Users save HOME, OFFICE, or custom named spots.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, auth
from ..database import get_db
from ..models import User, SavedLocation

router = APIRouter(prefix="/locations", tags=["saved locations"])


@router.post("/", response_model=schemas.SavedLocationResponse, status_code=201)
async def save_location(
    location: schemas.SavedLocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Save a named location (HOME, OFFICE, or any custom label)."""
    db_loc = SavedLocation(
        user_id=current_user.id,
        label=location.label.upper(),
        name=location.name,
        address=location.address,
        lat=location.lat,
        lng=location.lng,
    )
    db.add(db_loc)
    await db.commit()
    await db.refresh(db_loc)
    return db_loc


@router.get("/", response_model=list[schemas.SavedLocationResponse])
async def get_my_locations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    result = await db.execute(
        select(SavedLocation).where(SavedLocation.user_id == current_user.id)
    )
    return result.scalars().all()


@router.delete("/{location_id}", status_code=204)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    result = await db.execute(
        select(SavedLocation).where(
            SavedLocation.id == location_id,
            SavedLocation.user_id == current_user.id,
        )
    )
    loc = result.scalars().first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found.")
    await db.delete(loc)
    await db.commit()
