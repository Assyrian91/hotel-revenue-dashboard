import pandas as pd
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

DB_PATH = "data/processed/hotel.db"

def transform() -> tuple[pd.DataFrame, pd.DataFrame]:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM raw_bookings", conn)
    conn.close()

    log.info("Transforming data...")

    # Parse dates
    df["check_in_date"]  = pd.to_datetime(df["check_in_date"])
    df["check_out_date"] = pd.to_datetime(df["check_out_date"])

    # Drop nulls
    before = len(df)
    df.dropna(subset=["rate_paid", "room_type", "check_in_date"], inplace=True)
    log.info(f"Dropped {before - len(df)} rows with nulls")

    # Enforce types
    df["rate_paid"]      = df["rate_paid"].astype(float).round(2)
    df["total_revenue"]  = df["total_revenue"].astype(float).round(2)
    df["reservation_id"] = df["reservation_id"].astype(int)

    # ── Fact table ──────────────────────────────────────
    fact_bookings = df[[
        "reservation_id", "check_in_date", "check_out_date",
        "room_type", "rate_paid", "total_revenue",
        "booking_channel", "stay_length_nights",
        "rooms_available", "hotel_total_rooms"
    ]].copy()

    # ── Dimension: date ─────────────────────────────────
    all_dates = pd.date_range(df["check_in_date"].min(), df["check_in_date"].max(), freq="D")
    dim_date = pd.DataFrame({"date": all_dates})
    dim_date["year"]       = dim_date["date"].dt.year
    dim_date["month"]      = dim_date["date"].dt.month
    dim_date["month_name"] = dim_date["date"].dt.strftime("%B")
    dim_date["week"]       = dim_date["date"].dt.isocalendar().week.astype(int)
    dim_date["day_of_week"]= dim_date["date"].dt.day_name()
    dim_date["quarter"]    = dim_date["date"].dt.quarter
    dim_date["is_weekend"] = dim_date["date"].dt.weekday >= 4

    log.info(f"fact_bookings: {len(fact_bookings):,} rows | dim_date: {len(dim_date)} rows")
    return fact_bookings, dim_date

if __name__ == "__main__":
    fact, dim = transform()
    print(fact.head(2).to_string())