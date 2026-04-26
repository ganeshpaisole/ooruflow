"""
Push notification + email helpers.
Configure credentials via environment variables (see .env.example).
"""
import os
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@ooruflow.com")


async def send_push(fcm_token: str, title: str, body: str, data: dict = None):
    if not FCM_SERVER_KEY or not fcm_token:
        logger.warning("FCM not configured or no token — skipping push.")
        return
    payload = {
        "to": fcm_token,
        "notification": {"title": title, "body": body},
        "data": data or {},
    }
    headers = {"Authorization": f"key={FCM_SERVER_KEY}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://fcm.googleapis.com/fcm/send", json=payload, headers=headers)
        if resp.status_code != 200:
            logger.error(f"FCM error {resp.status_code}: {resp.text}")


async def send_email(to_email: str, subject: str, body: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping email.")
        return
    try:
        import aiosmtplib
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        await aiosmtplib.send(
            msg, hostname=SMTP_HOST, port=SMTP_PORT,
            username=SMTP_USER, password=SMTP_PASSWORD, start_tls=True,
        )
    except Exception as e:
        logger.error(f"Email failed: {e}")


# ── Notification templates ─────────────────────────────────────────────────

async def notify_ride_confirmed(user_email: str, fcm_token: Optional[str], ride_id: int):
    await send_push(
        fcm_token or "", "Ride Confirmed! 🚗",
        f"Your ride #{ride_id} is confirmed for tomorrow.",
        {"ride_id": str(ride_id), "event": "ride_confirmed"},
    )
    await send_email(
        user_email, "OoruFlow — Ride confirmed!",
        f"Your ride #{ride_id} has been matched and is confirmed for tomorrow. Have a smooth commute!",
    )


async def notify_driver_new_ride(fcm_token: Optional[str], ride_id: int):
    await send_push(
        fcm_token or "", "New Ride Assigned 📍",
        f"You have been assigned ride #{ride_id} for tomorrow.",
        {"ride_id": str(ride_id), "event": "ride_assigned"},
    )


async def notify_ride_starting(fcm_token: Optional[str], ride_id: int, driver_name: str):
    await send_push(
        fcm_token or "", "Driver on the way! 🚗",
        f"{driver_name} is heading to your pickup for ride #{ride_id}.",
        {"ride_id": str(ride_id), "event": "driver_en_route"},
    )


async def notify_ride_completed(fcm_token: Optional[str], ride_id: int):
    await send_push(
        fcm_token or "", "Ride Complete ✅",
        f"Ride #{ride_id} is complete. Rate your experience!",
        {"ride_id": str(ride_id), "event": "ride_completed"},
    )
