from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pytz

from . import models, schemas


# ── Rides ──────────────────────────────────────────────────────────────────

async def create_ride(db: AsyncSession, ride: schemas.ScheduledRideCreate, user_id: int):
    from . import utils
    deadline_ist = utils.get_ist_deadline(ride.slot_start)

    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    if now_ist >= deadline_ist:
        return None

    deadline_utc = deadline_ist.astimezone(pytz.UTC).replace(tzinfo=None)
    slot_start_utc = ride.slot_start.astimezone(pytz.UTC).replace(tzinfo=None)
    slot_end_utc = ride.slot_end.astimezone(pytz.UTC).replace(tzinfo=None)

    db_ride = models.ScheduledRide(
        user_id=user_id,
        ride_type=ride.ride_type,
        pickup_location=ride.pickup_location,
        dropoff_location=ride.dropoff_location,
        pickup_lat=ride.pickup_lat,
        pickup_lng=ride.pickup_lng,
        dropoff_lat=ride.dropoff_lat,
        dropoff_lng=ride.dropoff_lng,
        slot_start=slot_start_utc,
        slot_end=slot_end_utc,
        confirmation_deadline=deadline_utc,
        status=models.RideStatus.PENDING,
        created_at=datetime.utcnow(),
    )
    db.add(db_ride)
    await db.commit()
    await db.refresh(db_ride)
    return db_ride


async def create_ride_from_recurring(db: AsyncSession, fields: dict):
    """Bypass deadline check — used by the recurring-rides Celery task."""
    db_ride = models.ScheduledRide(**fields, created_at=datetime.utcnow())
    db.add(db_ride)
    await db.commit()
    await db.refresh(db_ride)
    return db_ride


async def get_ride_by_id(db: AsyncSession, ride_id: int):
    result = await db.execute(
        select(models.ScheduledRide).where(models.ScheduledRide.id == ride_id)
    )
    return result.scalars().first()


async def get_user_rides(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.ScheduledRide)
        .where(models.ScheduledRide.user_id == user_id)
        .order_by(models.ScheduledRide.slot_start.desc())
    )
    return result.scalars().all()


async def cancel_ride(db: AsyncSession, ride_id: int, user_id: int):
    ride = await get_ride_by_id(db, ride_id)
    if not ride or ride.user_id != user_id:
        return None
    if ride.status in (models.RideStatus.COMPLETED, models.RideStatus.CANCELLED):
        return None
    ride.status = models.RideStatus.CANCELLED
    await db.commit()
    await db.refresh(ride)
    return ride


async def update_ride_status(db: AsyncSession, ride_id: int, status: models.RideStatus):
    ride = await get_ride_by_id(db, ride_id)
    if not ride:
        return None
    ride.status = status
    await db.commit()
    await db.refresh(ride)
    return ride


async def get_pending_rides_for_date(db: AsyncSession, target_date: date):
    """Used by the matching engine — get all PENDING rides scheduled on target_date."""
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())
    result = await db.execute(
        select(models.ScheduledRide).where(
            models.ScheduledRide.status == models.RideStatus.PENDING,
            models.ScheduledRide.slot_start >= start,
            models.ScheduledRide.slot_start <= end,
        )
    )
    return result.scalars().all()


# ── Users ──────────────────────────────────────────────────────────────────

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    from . import auth
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=auth.get_password_hash(user.password),
        phone=user.phone,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()


async def update_user_fcm_token(db: AsyncSession, user_id: int, fcm_token: str):
    user = await get_user_by_id(db, user_id)
    if user:
        user.fcm_token = fcm_token
        await db.commit()
    return user


# ── Drivers ────────────────────────────────────────────────────────────────

async def create_driver(db: AsyncSession, driver: schemas.DriverCreate, user_id: int):
    db_driver = models.Driver(
        user_id=user_id,
        vehicle_number=driver.vehicle_number,
        vehicle_model=driver.vehicle_model,
        vehicle_type=driver.vehicle_type,
        license_number=driver.license_number,
        created_at=datetime.utcnow(),
    )
    db.add(db_driver)
    user = await get_user_by_id(db, user_id)
    if user:
        user.role = models.UserRole.DRIVER
    await db.commit()
    await db.refresh(db_driver)
    return db_driver


async def get_driver_by_id(db: AsyncSession, driver_id: int):
    result = await db.execute(select(models.Driver).where(models.Driver.id == driver_id))
    return result.scalars().first()


async def get_driver_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Driver).where(models.Driver.user_id == user_id))
    return result.scalars().first()


async def get_available_drivers(db: AsyncSession):
    result = await db.execute(
        select(models.Driver).where(models.Driver.status == models.DriverStatus.ONLINE)
    )
    return result.scalars().all()


async def update_driver_location(db: AsyncSession, driver_id: int, lat: float, lng: float):
    driver = await get_driver_by_id(db, driver_id)
    if driver:
        driver.current_lat = lat
        driver.current_lng = lng
        await db.commit()
    return driver


async def update_driver_status(db: AsyncSession, driver_id: int, status: models.DriverStatus):
    driver = await get_driver_by_id(db, driver_id)
    if driver:
        driver.status = status
        await db.commit()
        await db.refresh(driver)
    return driver


async def approve_driver(db: AsyncSession, driver_id: int):
    return await update_driver_status(db, driver_id, models.DriverStatus.APPROVED)


# ── Recurring Rides ────────────────────────────────────────────────────────

async def create_recurring_ride(db: AsyncSession, recurring: schemas.RecurringRideCreate, user_id: int):
    db_r = models.RecurringRide(
        user_id=user_id,
        pickup_location=recurring.pickup_location,
        dropoff_location=recurring.dropoff_location,
        pickup_lat=recurring.pickup_lat,
        pickup_lng=recurring.pickup_lng,
        dropoff_lat=recurring.dropoff_lat,
        dropoff_lng=recurring.dropoff_lng,
        slot_start_time=recurring.slot_start_time,
        slot_end_time=recurring.slot_end_time,
        days_of_week=recurring.days_of_week,
        ride_type=recurring.ride_type,
        created_at=datetime.utcnow(),
    )
    db.add(db_r)
    await db.commit()
    await db.refresh(db_r)
    return db_r


async def get_user_recurring_rides(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.RecurringRide).where(
            models.RecurringRide.user_id == user_id,
            models.RecurringRide.is_active == True,
        )
    )
    return result.scalars().all()


async def deactivate_recurring_ride(db: AsyncSession, recurring_id: int, user_id: int):
    result = await db.execute(
        select(models.RecurringRide).where(
            models.RecurringRide.id == recurring_id,
            models.RecurringRide.user_id == user_id,
        )
    )
    r = result.scalars().first()
    if r:
        r.is_active = False
        await db.commit()
    return r


async def get_all_active_recurring_rides(db: AsyncSession):
    result = await db.execute(
        select(models.RecurringRide).where(models.RecurringRide.is_active == True)
    )
    return result.scalars().all()


# ── Driver Earnings ────────────────────────────────────────────────────────

async def create_driver_earning(db: AsyncSession, driver_id: int, ride_id: int, amount: float):
    earning = models.DriverEarning(
        driver_id=driver_id,
        ride_id=ride_id,
        amount=amount,
        date=datetime.utcnow(),
    )
    db.add(earning)
    await db.commit()
    await db.refresh(earning)
    return earning


async def get_driver_earnings(db: AsyncSession, driver_id: int, since: datetime = None):
    query = select(models.DriverEarning).where(models.DriverEarning.driver_id == driver_id)
    if since:
        query = query.where(models.DriverEarning.date >= since)
    result = await db.execute(query.order_by(models.DriverEarning.date.desc()))
    return result.scalars().all()


# ── Ratings ────────────────────────────────────────────────────────────────

async def create_rating(db: AsyncSession, rating: schemas.RatingCreate, rated_by_user_id: int):
    db_rating = models.Rating(
        ride_id=rating.ride_id,
        rated_by_user_id=rated_by_user_id,
        rated_user_id=rating.rated_user_id,
        stars=rating.stars,
        comment=rating.comment,
        created_at=datetime.utcnow(),
    )
    db.add(db_rating)
    await db.commit()
    await db.refresh(db_rating)
    return db_rating
