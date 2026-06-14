import sqlite3
import pandas as pd
import os

DB_PATH = "data/processed/hotel.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_daily_kpis() -> pd.DataFrame:
    """Returns daily Occupancy Rate, ADR, and RevPAR."""
    query = """
    SELECT
        date(f.check_in_date)          AS date,
        f.room_type,
        COUNT(f.reservation_id)        AS rooms_sold,
        f.rooms_available              AS rooms_available,
        ROUND(COUNT(f.reservation_id) * 100.0 / f.rooms_available, 2)
                                       AS occupancy_rate,
        ROUND(SUM(f.rate_paid) / COUNT(f.reservation_id), 2)
                                       AS adr,
        ROUND(
            (SUM(f.rate_paid) / COUNT(f.reservation_id))
            * (COUNT(f.reservation_id) * 1.0 / f.rooms_available),
        2)                             AS revpar,
        ROUND(SUM(f.total_revenue), 2) AS total_revenue
    FROM fact_bookings f
    GROUP BY date(f.check_in_date), f.room_type, f.rooms_available
    ORDER BY date(f.check_in_date)
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df

def get_monthly_kpis() -> pd.DataFrame:
    """Aggregated monthly KPIs across all room types."""
    query = """
    SELECT
        strftime('%Y-%m', f.check_in_date)  AS month,
        COUNT(f.reservation_id)             AS total_rooms_sold,
        SUM(f.rooms_available)              AS total_rooms_available,
        ROUND(COUNT(f.reservation_id) * 100.0 / SUM(f.rooms_available), 2)
                                            AS occupancy_rate,
        ROUND(SUM(f.rate_paid) / COUNT(f.reservation_id), 2)
                                            AS adr,
        ROUND(
            (SUM(f.rate_paid) / COUNT(f.reservation_id))
            * (COUNT(f.reservation_id) * 1.0 / SUM(f.rooms_available)),
        2)                                  AS revpar,
        ROUND(SUM(f.total_revenue), 2)      AS total_revenue
    FROM fact_bookings f
    GROUP BY strftime('%Y-%m', f.check_in_date)
    ORDER BY month
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_channel_kpis() -> pd.DataFrame:
    """Revenue and bookings broken down by booking channel."""
    query = """
    SELECT
        booking_channel,
        COUNT(reservation_id)             AS total_bookings,
        ROUND(SUM(total_revenue), 2)      AS total_revenue,
        ROUND(AVG(rate_paid), 2)          AS avg_rate,
        ROUND(AVG(stay_length_nights), 1) AS avg_stay
    FROM fact_bookings
    GROUP BY booking_channel
    ORDER BY total_revenue DESC
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def export_kpi_summary():
    """Export monthly KPIs to CSV for Power BI and dashboard use."""
    df = get_monthly_kpis()
    os.makedirs("data/processed", exist_ok=True)
    path = "data/processed/kpi_summary.csv"
    df.to_csv(path, index=False)
    print(f"✓ KPI summary saved to {path}")
    return df

if __name__ == "__main__":
    print("\n── Monthly KPIs ──")
    print(get_monthly_kpis().to_string(index=False))
    print("\n── Channel KPIs ──")
    print(get_channel_kpis().to_string(index=False))
    export_kpi_summary()