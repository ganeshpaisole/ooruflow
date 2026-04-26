"""
Razorpay payment integration.
Docs: https://razorpay.com/docs/payments/

Flow:
  1. POST /payments/create-order  → creates Razorpay order, returns order_id + amount
  2. Client completes payment in app/web using Razorpay SDK
  3. POST /payments/verify        → verifies HMAC signature, marks ride PAID
  4. Razorpay webhook (optional)  → for async payment status updates
"""
import hashlib
import hmac
import os
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, auth
from ..database import get_db
from ..fare import calculate_fare, calculate_distance_km
from ..models import User, PaymentStatus, RideStatus, ScheduledRide, Payment

router = APIRouter(prefix="/payments", tags=["payments"])

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_API = "https://api.razorpay.com/v1"


async def _razorpay_create_order(amount_paise: int, receipt: str) -> dict:
    """Call Razorpay Orders API. Amount is in paise (INR × 100)."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{RAZORPAY_API}/orders",
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
            json={"amount": amount_paise, "currency": "INR", "receipt": receipt},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Razorpay error: {resp.text}")
    return resp.json()


def _verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify Razorpay payment signature using HMAC-SHA256."""
    message = f"{order_id}|{payment_id}"
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/create-order", response_model=schemas.PaymentCreateResponse)
async def create_payment_order(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Create a Razorpay order for a confirmed ride.
    Returns order_id to pass into the Razorpay SDK on the client.
    """
    if not RAZORPAY_KEY_ID:
        raise HTTPException(status_code=503, detail="Payment gateway not configured.")

    ride = await crud.get_ride_by_id(db, ride_id)
    if not ride or ride.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Ride not found.")
    if ride.status not in (RideStatus.PENDING, RideStatus.CONFIRMED):
        raise HTTPException(status_code=400, detail="Ride is not payable.")
    if ride.payment_status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Ride already paid.")

    # Calculate fare if not already set
    fare = ride.fare
    if fare is None:
        if all([ride.pickup_lat, ride.pickup_lng, ride.dropoff_lat, ride.dropoff_lng]):
            dist = calculate_distance_km(
                ride.pickup_lat, ride.pickup_lng,
                ride.dropoff_lat, ride.dropoff_lng,
            )
            fare = calculate_fare(dist, ride.ride_type, ride.slot_start)
            ride.fare = fare
            await db.commit()
        else:
            raise HTTPException(status_code=400, detail="Fare not yet calculated. Coordinates required.")

    amount_paise = int(fare * 100)
    rz_order = await _razorpay_create_order(amount_paise, receipt=f"ride_{ride_id}")

    # Persist Razorpay order in Payment table
    payment = Payment(
        ride_id=ride_id,
        user_id=current_user.id,
        razorpay_order_id=rz_order["id"],
        amount=fare,
        status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    ride.razorpay_order_id = rz_order["id"]
    await db.commit()

    return {
        "razorpay_order_id": rz_order["id"],
        "amount": fare,
        "currency": "INR",
        "ride_id": ride_id,
    }


@router.post("/verify", response_model=schemas.PaymentResponse)
async def verify_payment(
    payload: schemas.PaymentVerify,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    """
    Verify Razorpay payment signature after client-side checkout completes.
    Marks the ride and payment as PAID.
    """
    if not _verify_signature(
        payload.razorpay_order_id,
        payload.razorpay_payment_id,
        payload.razorpay_signature,
    ):
        raise HTTPException(status_code=400, detail="Invalid payment signature.")

    from sqlalchemy import select
    result = await db.execute(
        select(Payment).where(Payment.razorpay_order_id == payload.razorpay_order_id)
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found.")

    payment.razorpay_payment_id = payload.razorpay_payment_id
    payment.status = PaymentStatus.PAID

    ride = await crud.get_ride_by_id(db, payment.ride_id)
    if ride:
        ride.payment_status = PaymentStatus.PAID

    await db.commit()
    await db.refresh(payment)
    return payment


@router.post("/webhook")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Razorpay webhook endpoint.
    Configure in Razorpay Dashboard → Webhooks → URL: /payments/webhook
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")

    event = await request.json()
    if event.get("event") == "payment.captured":
        payment_data = event["payload"]["payment"]["entity"]
        order_id = payment_data.get("order_id")
        payment_id = payment_data.get("id")

        from sqlalchemy import select
        result = await db.execute(
            select(Payment).where(Payment.razorpay_order_id == order_id)
        )
        payment = result.scalars().first()
        if payment and payment.status != PaymentStatus.PAID:
            payment.razorpay_payment_id = payment_id
            payment.status = PaymentStatus.PAID
            ride = await crud.get_ride_by_id(db, payment.ride_id)
            if ride:
                ride.payment_status = PaymentStatus.PAID
            await db.commit()

    return {"status": "ok"}
