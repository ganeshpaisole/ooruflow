from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, auth
from ..database import get_db
from ..models import User, DriverStatus

router = APIRouter(prefix="/drivers", tags=["drivers"])


def _require_driver_role(current_user: User):
    """Raise 403 if the user does not have a driver profile status that allows action."""
    pass  # profile existence is checked per-endpoint


@router.post("/register", response_model=schemas.DriverResponse, status_code=201)
async def register_as_driver(
    driver_data: schemas.DriverCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Register the authenticated user as a driver. Pending admin approval."""
    existing = await crud.get_driver_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Driver profile already exists.")
    return await crud.create_driver(db, driver_data, current_user.id)


@router.get("/me", response_model=schemas.DriverResponse)
async def get_my_driver_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    driver = await crud.get_driver_by_user_id(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found.")
    return driver


@router.patch("/me/location")
async def update_my_location(
    location: schemas.DriverLocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Update real-time GPS coordinates (called by driver app every ~5 s)."""
    driver = await crud.get_driver_by_user_id(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found.")
    await crud.update_driver_location(db, driver.id, location.lat, location.lng)
    return {"message": "Location updated."}


@router.patch("/me/status", response_model=schemas.DriverResponse)
async def update_my_status(
    status_update: schemas.DriverStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Toggle ONLINE / OFFLINE. Only APPROVED drivers may go online."""
    driver = await crud.get_driver_by_user_id(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found.")
    if driver.status == DriverStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=403, detail="Your account is pending admin approval.")
    if driver.status == DriverStatus.SUSPENDED:
        raise HTTPException(status_code=403, detail="Your account has been suspended.")
    return await crud.update_driver_status(db, driver.id, status_update.status)


@router.get("/me/earnings", response_model=schemas.EarningsSummary)
async def get_my_earnings(
    period: str = "week",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Get earnings summary. period = 'week' | 'month' | 'all'"""
    driver = await crud.get_driver_by_user_id(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found.")

    since = None
    if period == "week":
        since = datetime.utcnow() - timedelta(days=7)
    elif period == "month":
        since = datetime.utcnow() - timedelta(days=30)

    earnings = await crud.get_driver_earnings(db, driver.id, since)
    return {
        "total_earnings": round(sum(e.amount for e in earnings), 2),
        "total_rides": len(earnings),
        "earnings": earnings,
    }
