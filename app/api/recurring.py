from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, auth
from ..database import get_db
from ..models import User

router = APIRouter(prefix="/recurring", tags=["recurring rides"])


@router.post("/", response_model=schemas.RecurringRideResponse, status_code=201)
async def create_recurring(
    recurring: schemas.RecurringRideCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Create a weekly recurring ride schedule.
    The system auto-books a ride at 12:01 AM IST each day that matches days_of_week.

    days_of_week example: "MON,TUE,WED,THU,FRI"
    slot_start_time / slot_end_time format: "HH:MM" (IST, 24-hour)
    """
    return await crud.create_recurring_ride(db, recurring, current_user.id)


@router.get("/", response_model=list[schemas.RecurringRideResponse])
async def list_my_recurring(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    return await crud.get_user_recurring_rides(db, current_user.id)


@router.delete("/{recurring_id}", status_code=204)
async def cancel_recurring(
    recurring_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """Deactivate a recurring schedule (won't affect already-created rides)."""
    result = await crud.deactivate_recurring_ride(db, recurring_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Recurring ride not found.")
