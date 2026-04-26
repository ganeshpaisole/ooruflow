"""
Fare calculation engine for OoruFlow.
Bengaluru-specific pricing with peak-hour surge.
"""
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import pytz
from .models import RideType

# ── Pricing constants ──────────────────────────────────────────────────────
BASE_FARE = 50.0            # INR — minimum fare
PER_KM_RATE = 12.0          # INR per km
PEAK_SURGE = 1.5            # 1.5x during peak hours
POOL_FACTOR = 0.65          # Pool riders pay 65% of solo fare (each)
DRIVER_SHARE = 0.80         # Driver keeps 80% of fare


def is_peak_hour(dt: datetime) -> bool:
    """Morning 8–10 AM IST and evening 5–8 PM IST are surge hours."""
    ist = pytz.timezone('Asia/Kolkata')
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    hour = dt.astimezone(ist).hour
    return (8 <= hour < 10) or (17 <= hour < 20)


def calculate_distance_km(
    pickup_lat: float, pickup_lng: float,
    dropoff_lat: float, dropoff_lng: float,
) -> float:
    """Haversine great-circle distance in km."""
    R = 6371
    lat1, lon1 = radians(pickup_lat), radians(pickup_lng)
    lat2, lon2 = radians(dropoff_lat), radians(dropoff_lng)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def calculate_fare(
    distance_km: float,
    ride_type: RideType,
    slot_start: datetime,
    num_passengers: int = 1,
) -> float:
    """
    Returns fare per rider in INR.
    Pool rides apply a discount and are split across confirmed passengers.
    """
    fare = BASE_FARE + (distance_km * PER_KM_RATE)
    if is_peak_hour(slot_start):
        fare *= PEAK_SURGE
    if ride_type == RideType.POOL:
        fare = (fare * POOL_FACTOR) / max(num_passengers, 1)
    return round(fare, 2)


def calculate_driver_payout(fare: float) -> float:
    return round(fare * DRIVER_SHARE, 2)
