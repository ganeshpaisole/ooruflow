"""
Celery background tasks.

Run the worker:   celery -A app.tasks worker --loglevel=info
Run the scheduler: celery -A app.tasks beat --loglevel=info
"""
import asyncio
import logging
from datetime import datetime, timedelta, time

import pytz

from .celery_app import celery_app

logger = logging.getLogger(__name__)


def _run(coro):
    """Run an async coroutine inside a synchronous Celery task."""
    return asyncio.run(coro)


# ── Ride matching ──────────────────────────────────────────────────────────

@celery_app.task(name="app.tasks.match_and_confirm_rides")
def match_and_confirm_rides():
    """
    Triggered daily at 8 PM IST.
    1. Fetch all PENDING rides for tomorrow.
    2. Assign available ONLINE drivers (round-robin; future: proximity matching).
    3. Calculate fares.
    4. Mark rides CONFIRMED and send notifications.
    """
    _run(_match_async())


async def _match_async():
    from .database import AsyncSessionLocal
    from . import crud, notifications
    from .fare import calculate_fare, calculate_distance_km
    from .models import RideStatus

    ist = pytz.timezone('Asia/Kolkata')
    tomorrow = (datetime.now(ist) + timedelta(days=1)).date()

    async with AsyncSessionLocal() as db:
        pending = await crud.get_pending_rides_for_date(db, tomorrow)
        drivers = await crud.get_available_drivers(db)

        logger.info(f"Matching engine: {len(pending)} rides, {len(drivers)} drivers available")

        if not drivers:
            logger.warning("No online drivers — rides remain PENDING.")
            return

        for i, ride in enumerate(pending):
            driver = drivers[i % len(drivers)]

            if all([ride.pickup_lat, ride.pickup_lng, ride.dropoff_lat, ride.dropoff_lng]):
                dist = calculate_distance_km(
                    ride.pickup_lat, ride.pickup_lng,
                    ride.dropoff_lat, ride.dropoff_lng,
                )
                ride.fare = calculate_fare(dist, ride.ride_type, ride.slot_start)

            ride.driver_id = driver.id
            ride.status = RideStatus.CONFIRMED

        await db.commit()

        # Notify riders and drivers
        for ride in pending:
            user = await crud.get_user_by_id(db, ride.user_id)
            if user:
                await notifications.notify_ride_confirmed(user.email, user.fcm_token, ride.id)

            if ride.driver_id:
                driver = await crud.get_driver_by_id(db, ride.driver_id)
                if driver:
                    driver_user = await crud.get_user_by_id(db, driver.user_id)
                    if driver_user:
                        await notifications.notify_driver_new_ride(driver_user.fcm_token, ride.id)

    logger.info(f"Matched and confirmed {len(pending)} rides for {tomorrow}.")


# ── Recurring rides ────────────────────────────────────────────────────────

@celery_app.task(name="app.tasks.create_recurring_rides_for_tomorrow")
def create_recurring_rides_for_tomorrow():
    """
    Triggered daily at 12:01 AM IST.
    Reads all active recurring schedules and creates ScheduledRide rows for tomorrow
    if tomorrow falls on a scheduled day.
    """
    _run(_create_recurring_async())


async def _create_recurring_async():
    from .database import AsyncSessionLocal
    from . import crud
    from .models import RideStatus
    from .utils import get_ist_deadline

    ist = pytz.timezone('Asia/Kolkata')
    tomorrow = (datetime.now(ist) + timedelta(days=1)).date()
    day_abbr = tomorrow.strftime("%a").upper()  # MON, TUE …

    async with AsyncSessionLocal() as db:
        schedules = await crud.get_all_active_recurring_rides(db)
        created = 0

        for r in schedules:
            if day_abbr not in r.days_of_week.upper():
                continue

            h_start, m_start = map(int, r.slot_start_time.split(":"))
            h_end, m_end = map(int, r.slot_end_time.split(":"))

            slot_start_ist = ist.localize(datetime.combine(tomorrow, time(h_start, m_start)))
            slot_end_ist = ist.localize(datetime.combine(tomorrow, time(h_end, m_end)))
            deadline_ist = get_ist_deadline(slot_start_ist)

            await crud.create_ride_from_recurring(db, {
                "user_id": r.user_id,
                "ride_type": r.ride_type,
                "pickup_location": r.pickup_location,
                "dropoff_location": r.dropoff_location,
                "pickup_lat": r.pickup_lat,
                "pickup_lng": r.pickup_lng,
                "dropoff_lat": r.dropoff_lat,
                "dropoff_lng": r.dropoff_lng,
                "slot_start": slot_start_ist.astimezone(pytz.UTC).replace(tzinfo=None),
                "slot_end": slot_end_ist.astimezone(pytz.UTC).replace(tzinfo=None),
                "confirmation_deadline": deadline_ist.astimezone(pytz.UTC).replace(tzinfo=None),
                "status": RideStatus.PENDING,
            })
            created += 1

    logger.info(f"Created {created} recurring rides for {tomorrow} ({day_abbr}).")
