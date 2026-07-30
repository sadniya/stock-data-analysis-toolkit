"""
STEP 2: Load the cleaned CSV into a local SQLite database.
Run this after 01_fetch_and_clean.py.

Concepts practiced: to_sql(), basic schema thinking (even a single table
benefits from correct types and a primary key).
"""

import sqlite3
import pandas as pd

CSV_PATH = "prices_clean.csv"
DB_PATH = "stocks.db"


def load_csv_to_sql():
    df = pd.read_csv(CSV_PATH, parse_dates=["date"])

    conn = sqlite3.connect(DB_PATH)

    # Write the table. if_exists="replace" keeps this repeatable while you're
    # experimenting -- in a real system you'd use upserts instead.
    df.to_sql("daily_prices", conn, if_exists="replace", index=False)

    # A composite index makes your per-ticker, per-date queries fast --
    # worth doing even in a small toy database, it's a habit worth building.
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ticker_date ON daily_prices(ticker, date)")
    conn.commit()

    # sanity check
    count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
    tickers = conn.execute("SELECT COUNT(DISTINCT ticker) FROM daily_prices").fetchone()[0]
    print(f"Loaded {count} rows across {tickers} tickers into {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    load_csv_to_sql()
