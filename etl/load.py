import sqlite3
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

DB_PATH = "data/processed/hotel.db"

def load(fact_bookings: pd.DataFrame, dim_date: pd.DataFrame) -> None:
    conn = sqlite3.connect(DB_PATH)
    fact_bookings.to_sql("fact_bookings", conn, if_exists="replace", index=False)
    dim_date.to_sql("dim_date",       conn, if_exists="replace", index=False)
    conn.close()
    log.info("Loaded fact_bookings and dim_date into hotel.db ✓")

if __name__ == "__main__":
    from transform import transform
    fact, dim = transform()
    load(fact, dim)