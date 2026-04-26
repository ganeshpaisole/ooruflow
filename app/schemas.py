from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime, timedelta
from typing import Optional, List
from .models import RideStatus, RideType, PaymentStatus, DriverStatus, VehicleType, UserRole


# ── User ───────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    fcm_token: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str


# ── Driver ─────────────────────────────────────────────────────────────────

class DriverCreate(BaseModel):
    vehicle_number: str
    vehicle_model: str
    vehicle_type: VehicleType
    license_number: str

class DriverLocationUpdate(BaseModel):
    lat: float
    lng: float

class DriverStatusUpdate(BaseModel):
    status: DriverStatus

class DriverResponse(BaseModel):
    id: int
    user_id: int
    vehicle_number: str
    vehicle_model: str
    vehicle_type: VehicleType
    license_number: str
    status: DriverStatus
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    avg_rating: float
    total_rides: int

    model_config = ConfigDict(from_attributes=True)


# ── Saved Locations ────────────────────────────────────────────────────────

class SavedLocationCreate(BaseModel):
    label: str
    name: str
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class SavedLocationResponse(SavedLocationCreate):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


# ── Rides ──────────────────────────────────────────────────────────────────

class ScheduledRideBase(BaseModel):
    pickup_location: str
    dropoff_location: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    slot_start: datetime
    slot_end: datetime
    ride_type: RideType = RideType.SOLO

class ScheduledRideCreate(ScheduledRideBase):
    @field_validator('slot_end')
    @classmethod
    def check_three_hour_window(cls, v, info):
        if 'slot_start' in info.data and v:
            diff = v - info.data['slot_start']
            if diff > timedelta(hours=3) or diff <= timedelta(0):
                raise ValueError("Slot window must be between 0 and 3 hours.")
        return v

class ScheduledRideResponse(ScheduledRideBase):
    id: int
    user_id: int
    driver_id: Optional[int] = None
    confirmation_deadline: datetime
    status: RideStatus
    fare: Optional[float] = None
    payment_status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RideStatusUpdate(BaseModel):
    status: RideStatus


# ── Recurring Rides ────────────────────────────────────────────────────────

class RecurringRideCreate(BaseModel):
    pickup_location: str
    dropoff_location: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    slot_start_time: str   # "HH:MM" IST
    slot_end_time: str     # "HH:MM" IST
    days_of_week: str      # "MON,TUE,WED,THU,FRI"
    ride_type: RideType = RideType.SOLO

class RecurringRideResponse(RecurringRideCreate):
    id: int
    user_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ── Payments ───────────────────────────────────────────────────────────────

class PaymentCreateResponse(BaseModel):
    razorpay_order_id: str
    amount: float
    currency: str = "INR"
    ride_id: int

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentResponse(BaseModel):
    id: int
    ride_id: int
    amount: float
    status: PaymentStatus
    razorpay_order_id: str

    model_config = ConfigDict(from_attributes=True)


# ── Ratings ────────────────────────────────────────────────────────────────

class RatingCreate(BaseModel):
    ride_id: int
    rated_user_id: int
    stars: int
    comment: Optional[str] = None

    @field_validator('stars')
    @classmethod
    def validate_stars(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Stars must be between 1 and 5.")
        return v

class RatingResponse(BaseModel):
    id: int
    ride_id: int
    rated_by_user_id: int
    rated_user_id: int
    stars: int
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ── Driver Earnings ────────────────────────────────────────────────────────

class DriverEarningResponse(BaseModel):
    id: int
    ride_id: int
    amount: float
    date: datetime

    model_config = ConfigDict(from_attributes=True)

class EarningsSummary(BaseModel):
    total_earnings: float
    total_rides: int
    earnings: List[DriverEarningResponse]
