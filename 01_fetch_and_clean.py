"""
STEP 1: Fetch stock data and clean it with Pandas.
Run this first. It downloads ~2 years of daily prices for a basket of
stocks and saves ONE clean CSV that later scripts will reuse.

Concepts practiced: DataFrame merging, reshaping (melt), handling missing
values, working with dates.
"""

import pandas as pd
import yfinance as yf

# Pick a small, mixed basket so your queries later actually have variety
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JPM", "XOM", "PFE", "KO", "NVDA"]
START = "2023-01-01"
END = "2025-01-01"


def fetch_raw_prices() -> pd.DataFrame:
    """Download OHLCV data for every ticker and stack it into ONE long
    DataFrame with columns: date, ticker, open, high, low, close, volume.
    """
    frames = []
    for ticker in TICKERS:
        print(f"Downloading {ticker}...")
        df = yf.download(ticker, start=START, end=END, progress=False)
        if df.empty:
            print(f"  WARNING: no data returned for {ticker}, skipping")
            continue

        # yfinance can return MultiIndex columns when downloading singly in
        # newer versions -- flatten just in case
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df["ticker"] = ticker
        df = df.rename(columns={
            "Date": "date", "Open": "open", "High": "high",
            "Low": "low", "Close": "close", "Volume": "volume",
        })
        frames.append(df[["date", "ticker", "open", "high", "low", "close", "volume"]])

    return pd.concat(frames, ignore_index=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Real-world cleanup: drop dupes, sort, fix dtypes, report NaNs."""
    df = df.drop_duplicates(subset=["date", "ticker"])
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])

    # Report (don't silently hide) any missing values before deciding what to do
    nan_counts = df.isna().sum()
    if nan_counts.sum() > 0:
        print("\nMissing values found:\n", nan_counts[nan_counts > 0])
        df = df.dropna(subset=["close"])  # close price is essential, drop rows missing it

    return df


def add_daily_return(df: pd.DataFrame) -> pd.DataFrame:
    """Add a daily % return column, computed per ticker (not across tickers!)."""
    df["daily_return"] = df.groupby("ticker")["close"].pct_change()
    return df


if __name__ == "__main__":
    raw = fetch_raw_prices()
    clean_df = clean(raw)
    final_df = add_daily_return(clean_df)

    out_path = "prices_clean.csv"
    final_df.to_csv(out_path, index=False)
    print(f"\nSaved {len(final_df)} rows for {final_df['ticker'].nunique()} tickers to {out_path}")
    print(final_df.head())
