import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import date, timedelta
import os

fake = Faker()
random.seed(42)
np.random.seed(42)

# ── Config ──────────────────────────────────────────────
START_DATE = date(2020, 1, 1)
END_DATE   = date(2026, 12, 31)
TOTAL_ROOMS = 120
ROOM_TYPES  = ["Standard", "Deluxe", "Suite", "Executive"]
ROOM_COUNTS = {"Standard": 60, "Deluxe": 35, "Suite": 15, "Executive": 10}
BASE_RATES  = {"Standard": 89, "Deluxe": 139, "Suite": 249, "Executive": 199}
CHANNELS    = ["Direct", "OTA (Booking.com)", "OTA (Expedia)", "Corporate", "Walk-in"]

def get_seasonal_multiplier(d: date) -> float:
    """Higher demand in summer and Dec holidays."""
    month = d.month
    if month in [6, 7, 8, 12]:
        return round(random.uniform(0.82, 0.97), 3)
    elif month in [1, 2, 11]:
        return round(random.uniform(0.42, 0.60), 3)
    else:
        return round(random.uniform(0.60, 0.78), 3)

def get_weekend_boost(d: date) -> float:
    return 1.15 if d.weekday() >= 4 else 1.0   # Fri/Sat/Sun

records = []
reservation_id = 1000

current = START_DATE
while current <= END_DATE:
    occ_rate = get_seasonal_multiplier(current) * get_weekend_boost(current)

    for room_type, room_count in ROOM_COUNTS.items():
        rooms_sold = int(room_count * occ_rate * random.uniform(0.9, 1.1))
        rooms_sold = min(rooms_sold, room_count)

        for _ in range(rooms_sold):
            stay_nights = random.choices([1, 2, 3, 4, 5, 7], weights=[30, 25, 20, 10, 8, 7])[0]
            check_out   = current + timedelta(days=stay_nights)
            base_rate   = BASE_RATES[room_type]
            rate_noise  = random.uniform(0.88, 1.18)
            rate_paid   = round(base_rate * rate_noise * (1 + (occ_rate - 0.6) * 0.3), 2)
            channel     = random.choices(CHANNELS, weights=[25, 30, 20, 15, 10])[0]

            records.append({
                "reservation_id":  reservation_id,
                "check_in_date":   current.isoformat(),
                "check_out_date":  check_out.isoformat(),
                "room_type":       room_type,
                "rate_paid":       rate_paid,
                "booking_channel": channel,
                "stay_length_nights": stay_nights,
                "total_revenue":   round(rate_paid * stay_nights, 2),
                "rooms_available": room_count,
                "hotel_total_rooms": TOTAL_ROOMS,
            })
            reservation_id += 1

    current += timedelta(days=1)

df = pd.DataFrame(records)
os.makedirs("data/raw", exist_ok=True)
out_path = "data/raw/bookings_raw.csv"
df.to_csv(out_path, index=False)

print(f"✓ Generated {len(df):,} booking records")
print(f"✓ Date range: {df['check_in_date'].min()} → {df['check_in_date'].max()}")
print(f"✓ Saved to: {out_path}")
print(df.head(3).to_string())
