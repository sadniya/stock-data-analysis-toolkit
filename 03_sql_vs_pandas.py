"""
STEP 3: The core exercise. Every question below is answered TWICE --
once with a SQL query, once with Pandas -- so you build fluency
translating between the two. This mapping is exactly what shows up in
data/ML interviews.

Run this after 02_load_to_sql.py.
"""

import sqlite3
import pandas as pd

DB_PATH = "stocks.db"
CSV_PATH = "prices_clean.csv"


def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def q1_avg_return_per_ticker(conn, df):
    """Q1: Average daily return per ticker, ranked highest to lowest."""
    section("Q1: Average daily return per ticker")

    sql = """
        SELECT ticker, AVG(daily_return) AS avg_return
        FROM daily_prices
        GROUP BY ticker
        ORDER BY avg_return DESC
    """
    print("--- SQL ---")
    print(pd.read_sql(sql, conn))

    print("\n--- Pandas ---")
    print(
        df.groupby("ticker")["daily_return"]
        .mean()
        .sort_values(ascending=False)
        .rename("avg_return")
    )


def q2_top5_volatile_days(conn, df):
    """Q2: Top 5 most volatile single days for EACH ticker.
    This is where SQL window functions and Pandas groupby+rank map 1:1.
    """
    section("Q2: Top 5 most volatile days per ticker (by |daily_return|)")

    sql = """
        WITH ranked AS (
            SELECT
                ticker, date, daily_return,
                RANK() OVER (
                    PARTITION BY ticker
                    ORDER BY ABS(daily_return) DESC
                ) AS rnk
            FROM daily_prices
            WHERE daily_return IS NOT NULL
        )
        SELECT ticker, date, daily_return
        FROM ranked
        WHERE rnk <= 5
        ORDER BY ticker, rnk
    """
    print("--- SQL (window function RANK) ---")
    print(pd.read_sql(sql, conn).head(15))

    print("\n--- Pandas (groupby + rank) ---")
    tmp = df.dropna(subset=["daily_return"]).copy()
    tmp["rnk"] = tmp.groupby("ticker")["daily_return"].transform(
        lambda x: x.abs().rank(ascending=False, method="min")
    )
    result = tmp[tmp["rnk"] <= 5].sort_values(["ticker", "rnk"])
    print(result[["ticker", "date", "daily_return"]].head(15))


def q3_consecutive_gains(conn, df):
    """Q3: Dates where a stock rose for 3 consecutive days in a row.
    SQL uses LAG() to look at prior rows; Pandas uses shift() -- same idea.
    """
    section("Q3: Stocks with 3 consecutive up-days")

    sql = """
        WITH flagged AS (
            SELECT
                ticker, date, daily_return,
                CASE WHEN daily_return > 0 THEN 1 ELSE 0 END AS is_up,
                LAG(CASE WHEN daily_return > 0 THEN 1 ELSE 0 END, 1) OVER (
                    PARTITION BY ticker ORDER BY date) AS up_1,
                LAG(CASE WHEN daily_return > 0 THEN 1 ELSE 0 END, 2) OVER (
                    PARTITION BY ticker ORDER BY date) AS up_2
            FROM daily_prices
        )
        SELECT ticker, date
        FROM flagged
        WHERE is_up = 1 AND up_1 = 1 AND up_2 = 1
        ORDER BY ticker, date
    """
    print("--- SQL (LAG) ---")
    result_sql = pd.read_sql(sql, conn)
    print(f"Found {len(result_sql)} such days. Sample:")
    print(result_sql.head(10))

    print("\n--- Pandas (shift) ---")
    tmp = df.copy()
    tmp["is_up"] = tmp["daily_return"] > 0
    tmp["up_1"] = tmp.groupby("ticker")["is_up"].shift(1)
    tmp["up_2"] = tmp.groupby("ticker")["is_up"].shift(2)
    result_pd = tmp[tmp["is_up"] & tmp["up_1"] & tmp["up_2"]][["ticker", "date"]]
    print(f"Found {len(result_pd)} such days. Sample:")
    print(result_pd.head(10))


def q4_best_sector_proxy(conn, df):
    """Q4: Which ticker had the highest cumulative return over the period?
    (A stand-in for 'best performer' -- cumulative product of (1+return).)
    """
    section("Q4: Highest total return over the whole period")

    print("--- SQL is awkward here on purpose ---")
    print("Cumulative compounding isn't natural in plain SQL -- this is a")
    print("good example of 'use the right tool': Pandas wins for this one.")

    print("\n--- Pandas ---")
    cum_return = (
        df.dropna(subset=["daily_return"])
        .groupby("ticker")["daily_return"]
        .apply(lambda x: (1 + x).prod() - 1)
        .sort_values(ascending=False)
    )
    print((cum_return * 100).round(2).rename("total_return_%"))


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_csv(CSV_PATH, parse_dates=["date"])

    q1_avg_return_per_ticker(conn, df)
    q2_top5_volatile_days(conn, df)
    q3_consecutive_gains(conn, df)
    q4_best_sector_proxy(conn, df)

    conn.close()
