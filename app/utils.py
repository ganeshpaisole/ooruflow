from datetime import datetime, time, timedelta
import pytz

def get_ist_deadline(ride_date_obj: datetime):
    """
    Calculates the 8 PM IST deadline on the day BEFORE the ride.
    """
    ist = pytz.timezone('Asia/Kolkata')
    # Day before the ride
    deadline_day = ride_date_obj.date() - timedelta(days=1)
    # 8:00 PM IST
    deadline_time = time(20, 0)
    
    localized_deadline = ist.localize(datetime.combine(deadline_day, deadline_time))
    return localized_deadline