"""
Admin-only API endpoints.
Protected by the 'admin' role — regular users get 403.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, auth
from ..database import get_db
from ..models import User, UserRole, Driver, DriverStatus, ScheduledRide, RideStatus, Payment, PaymentStatus

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: User = Depends(auth.get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user


# ── Stats ──────────────────────────────────────────────────────────────────

@router.get("/stats")
async def platform_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """High-level platform metrics."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_drivers = (await db.execute(select(func.count(Driver.id)))).scalar()
    online_drivers = (await db.execute(
        select(func.count(Driver.id)).where(Driver.status == DriverStatus.ONLINE)
    )).scalar()
    total_rides = (await db.execute(select(func.count(ScheduledRide.id)))).scalar()
    completed_rides = (await db.execute(
        select(func.count(ScheduledRide.id)).where(ScheduledRide.status == RideStatus.COMPLETED)
    )).scalar()
    total_revenue = (await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.PAID)
    )).scalar() or 0.0
    pending_approval = (await db.execute(
        select(func.count(Driver.id)).where(Driver.status == DriverStatus.PENDING_APPROVAL)
    )).scalar()

    return {
        "users": {"total": total_users},
        "drivers": {
            "total": total_drivers,
            "online": online_drivers,
            "pending_approval": pending_approval,
        },
        "rides": {"total": total_rides, "completed": completed_rides},
        "revenue": {"total_inr": round(total_revenue, 2)},
    }


# ── Driver management ──────────────────────────────────────────────────────

@router.get("/drivers", response_model=list[schemas.DriverResponse])
async def list_all_drivers(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = select(Driver)
    if status:
        try:
            query = query.where(Driver.status == DriverStatus[status.upper()])
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Unknown status '{status}'.")
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/drivers/{driver_id}/approve", response_model=schemas.DriverResponse)
async def approve_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Approve a driver so they can go ONLINE and receive rides."""
    driver = await crud.approve_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")
    return driver


@router.patch("/drivers/{driver_id}/suspend", response_model=schemas.DriverResponse)
async def suspend_driver(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    driver = await crud.update_driver_status(db, driver_id, DriverStatus.SUSPENDED)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")
    return driver


# ── User management ────────────────────────────────────────────────────────

@router.get("/users", response_model=list[schemas.UserResponse])
async def list_all_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = False
    await db.commit()
    return {"message": f"User {user_id} deactivated."}


# ── Ride management ────────────────────────────────────────────────────────

@router.get("/rides", response_model=list[schemas.ScheduledRideResponse])
async def list_all_rides(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = select(ScheduledRide).order_by(ScheduledRide.slot_start.desc())
    if status:
        try:
            query = query.where(ScheduledRide.status == RideStatus[status.upper()])
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Unknown status '{status}'.")
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/rides/{ride_id}/status")
async def override_ride_status(
    ride_id: int,
    update: schemas.RideStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admin override for ride status (e.g. resolve disputes)."""
    ride = await crud.update_ride_status(db, ride_id, update.status)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    return {"message": f"Ride {ride_id} status updated to {update.status.value}."}
