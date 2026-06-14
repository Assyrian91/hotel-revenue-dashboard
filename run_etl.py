import logging
from etl.extract   import extract, load_raw_to_db
from etl.transform import transform
from etl.load      import load

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

if __name__ == "__main__":
    log.info("══════════  ETL START  ══════════")
    df = extract()
    load_raw_to_db(df)
    fact, dim = transform()
    load(fact, dim)
    log.info("══════════  ETL DONE   ══════════")
    print("\n✓ hotel.db is ready in data/processed/")