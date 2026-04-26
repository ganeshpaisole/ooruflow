import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from .database import Base


# ── Enums ──────────────────────────────────────────────────────────────────

class UserRole(enum.Enum):
    RIDER = "rider"
    DRIVER = "driver"
    ADMIN = "admin"

class RideStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RideType(enum.Enum):
    SOLO = "solo"
    POOL = "pool"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class DriverStatus(enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    OFFLINE = "offline"
    ONLINE = "online"

class VehicleType(enum.Enum):
    BIKE = "bike"
    AUTO = "auto"
    SEDAN = "sedan"
    SUV = "suv"


# ── Models ─────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.RIDER)
    fcm_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    rides = relationship("ScheduledRide", back_populates="owner", foreign_keys="ScheduledRide.user_id")
    driver_profile = relationship("Driver", back_populates="user", uselist=False)
    saved_locations = relationship("SavedLocation", back_populates="user")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    vehicle_number = Column(String)
    vehicle_model = Column(String)
    vehicle_type = Column(Enum(VehicleType))
    license_number = Column(String)
    status = Column(Enum(DriverStatus), default=DriverStatus.PENDING_APPROVAL)
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    avg_rating = Column(Float, default=5.0)
    total_rides = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="driver_profile")
    rides = relationship("ScheduledRide", back_populates="driver")
    earnings = relationship("DriverEarning", back_populates="driver")


class ScheduledRide(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    ride_type = Column(Enum(RideType), default=RideType.SOLO)
    pickup_location = Column(String)
    dropoff_location = Column(String)
    pickup_lat = Column(Float, nullable=True)
    pickup_lng = Column(Float, nullable=True)
    dropoff_lat = Column(Float, nullable=True)
    dropoff_lng = Column(Float, nullable=True)
    slot_start = Column(DateTime)
    slot_end = Column(DateTime)
    confirmation_deadline = Column(DateTime)
    status = Column(Enum(RideStatus), default=RideStatus.PENDING)
    fare = Column(Float, nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    razorpay_order_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="rides", foreign_keys=[user_id])
    driver = relationship("Driver", back_populates="rides")
    passengers = relationship("RidePassenger", back_populates="ride")
    payment = relationship("Payment", back_populates="ride", uselist=False)
    ratings = relationship("Rating", back_populates="ride")


class RidePassenger(Base):
    """Joins multiple riders to a single POOL ride."""
    __tablename__ = "ride_passengers"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    pickup_location = Column(String)
    dropoff_location = Column(String)
    fare_share = Column(Float, nullable=True)

    ride = relationship("ScheduledRide", back_populates="passengers")
    user = relationship("User")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    razorpay_order_id = Column(String, unique=True, index=True)
    razorpay_payment_id = Column(String, nullable=True)
    amount = Column(Float)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    ride = relationship("ScheduledRide", back_populates="payment")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    rated_by_user_id = Column(Integer, ForeignKey("users.id"))
    rated_user_id = Column(Integer, ForeignKey("users.id"))
    stars = Column(Integer)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ride = relationship("ScheduledRide", back_populates="ratings")


class RecurringRide(Base):
    """User-defined weekly schedule that auto-creates rides each day at midnight."""
    __tablename__ = "recurring_rides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pickup_location = Column(String)
    dropoff_location = Column(String)
    pickup_lat = Column(Float, nullable=True)
    pickup_lng = Column(Float, nullable=True)
    dropoff_lat = Column(Float, nullable=True)
    dropoff_lng = Column(Float, nullable=True)
    slot_start_time = Column(String)    # "HH:MM" in IST
    slot_end_time = Column(String)      # "HH:MM" in IST
    days_of_week = Column(String)       # "MON,TUE,WED,THU,FRI"
    ride_type = Column(Enum(RideType), default=RideType.SOLO)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class SavedLocation(Base):
    __tablename__ = "saved_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    label = Column(String)      # HOME, OFFICE, OTHER
    name = Column(String)
    address = Column(String)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    user = relationship("User", back_populates="saved_locations")


class DriverEarning(Base):
    __tablename__ = "driver_earnings"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    ride_id = Column(Integer, ForeignKey("rides.id"), unique=True)
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver", back_populates="earnings")
