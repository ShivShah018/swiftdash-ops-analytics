"""
SwiftDash — MySQL Data Loader
Loads cleaned CSV files into MySQL database.
Uses SQLAlchemy for bulk insert.

Prerequisites:
- MySQL 8.0+ running locally or remotely
- Database 'swiftdash_analytics' created (run sql/01_schema.sql first)
- .env file with DB credentials (or use defaults below)
"""

import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

CLEAN_DIR = Path(__file__).resolve().parents[1] / "data" / "cleaned"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "swiftdash_analytics"),
}

FILES_TABLES = [
    ("customers_clean.csv", "customers"),
    ("restaurants_clean.csv", "restaurants"),
    ("drivers_clean.csv", "drivers"),
    ("orders_clean.csv", "orders"),
    ("order_items_clean.csv", "order_items"),
    ("delivery_logs_clean.csv", "delivery_logs"),
]


def get_engine():
    url = (
        f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(url)


def clear_tables(engine):
    """Truncate all tables in reverse dependency order."""
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for _, table in reversed(FILES_TABLES):
            conn.execute(text(f"TRUNCATE TABLE {table}"))
            print(f"  Truncated {table}")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


def load_data(engine):
    for file_name, table_name in FILES_TABLES:
        path = CLEAN_DIR / file_name
        if not path.exists():
            print(f"  [SKIP] {file_name} not found")
            continue
        df = pd.read_csv(path)
        rows = len(df)
        df.to_sql(
            table_name,
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000,
        )
        print(f"  [OK] {file_name} -> {table_name} ({rows} rows)")


def main():
    print("=" * 50)
    print("SwiftDash MySQL Data Loader")
    print("=" * 50)

    engine = get_engine()
    print(f"\nConnecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']} ...")

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  Connection successful")
    except Exception as e:
        print(f"  Connection failed: {e}")
        print("\nMake sure MySQL is running and the database is created.")
        print("Run sql/01_schema.sql first to create the database and tables.")
        return

    print("\nClearing existing data...")
    clear_tables(engine)

    print("\nLoading data...")
    load_data(engine)

    print("\n" + "=" * 50)
    print("Data loading complete! Run verification queries to confirm.")
    print("=" * 50)


if __name__ == "__main__":
    main()
