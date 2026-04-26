import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ooruflow",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"],
)

celery_app.conf.timezone = "UTC"

# ── Scheduled tasks ────────────────────────────────────────────────────────
celery_app.conf.beat_schedule = {
    # 8 PM IST = 14:30 UTC — match rides and notify users
    "match-rides-8pm-ist": {
        "task": "app.tasks.match_and_confirm_rides",
        "schedule": crontab(hour=14, minute=30),
    },
    # 12:01 AM IST = 18:31 UTC — auto-create tomorrow's recurring rides
    "create-recurring-rides-midnight": {
        "task": "app.tasks.create_recurring_rides_for_tomorrow",
        "schedule": crontab(hour=18, minute=31),
    },
}
