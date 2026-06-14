import pandas as pd
import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

DB_PATH  = "data/processed/hotel.db"
CSV_PATH = "data/raw/bookings_raw.csv"

def extract() -> pd.DataFrame:
    log.info("Extracting raw CSV...")
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Raw data not found at {CSV_PATH}. Run generate_data.py first.")
    df = pd.read_csv(CSV_PATH)
    log.info(f"Loaded {len(df):,} rows from {CSV_PATH}")
    return df

def load_raw_to_db(df: pd.DataFrame) -> None:
    os.makedirs("data/processed", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("raw_bookings", conn, if_exists="replace", index=False)
    conn.close()
    log.info(f"Raw data loaded into SQLite → {DB_PATH} (table: raw_bookings)")

if __name__ == "__main__":
    df = extract()
    load_raw_to_db(df)