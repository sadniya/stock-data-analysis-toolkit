"""
STEP 4: NumPy from scratch. You'll rebuild calculations you did with
Pandas shortcuts using raw NumPy arrays, then run a Monte Carlo price
simulation. This builds real intuition about *why* vectorized code
is fast, and is a common interview topic.

Run this after 01_fetch_and_clean.py (only needs the CSV, not SQL).
"""

import numpy as np
import pandas as pd

CSV_PATH = "prices_clean.csv"


def manual_daily_return(prices: np.ndarray) -> np.ndarray:
    """Reimplement pandas' pct_change() using pure NumPy slicing.
    return[t] = (price[t] - price[t-1]) / price[t-1]
    """
    returns = np.empty_like(prices, dtype=float)
    returns[0] = np.nan
    returns[1:] = (prices[1:] - prices[:-1]) / prices[:-1]
    return returns


def manual_rolling_mean(arr: np.ndarray, window: int) -> np.ndarray:
    """Reimplement pandas' .rolling(window).mean() with a sliding window,
    using cumulative sums so it stays O(n) instead of O(n * window).
    """
    n = len(arr)
    result = np.full(n, np.nan)
    csum = np.cumsum(np.insert(arr, 0, 0))
    for i in range(window - 1, n):
        result[i] = (csum[i + 1] - csum[i + 1 - window]) / window
    return result


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Correlation between tickers' daily returns using np.corrcoef.
    Requires reshaping the long DataFrame into a wide matrix first.
    """
    wide = df.pivot(index="date", columns="ticker", values="daily_return").dropna()
    corr = np.corrcoef(wide.values.T)
    return pd.DataFrame(corr, index=wide.columns, columns=wide.columns)


def monte_carlo_price_paths(
    start_price: float, daily_mean: float, daily_std: float,
    days: int = 30, simulations: int = 1000, seed: int = 42,
) -> np.ndarray:
    """Simulate `simulations` possible future price paths using the
    historical mean/std of daily returns as the random walk parameters.
    Returns an array of shape (simulations, days) of simulated prices.
    """
    rng = np.random.default_rng(seed)
    random_returns = rng.normal(loc=daily_mean, scale=daily_std, size=(simulations, days))
    growth_factors = 1 + random_returns
    cumulative_growth = np.cumprod(growth_factors, axis=1)
    price_paths = start_price * cumulative_growth
    return price_paths


if __name__ == "__main__":
    df = pd.read_csv(CSV_PATH, parse_dates=["date"])
    aapl = df[df["ticker"] == "AAPL"].sort_values("date").reset_index(drop=True)

    print("=" * 70)
    print("1) Manual daily return vs Pandas pct_change")
    print("=" * 70)
    manual = manual_daily_return(aapl["close"].values)
    pandas_version = aapl["close"].pct_change().values
    # nan != nan, so compare only the non-nan portion
    matches = np.allclose(manual[1:], pandas_version[1:])
    print(f"Manual NumPy result matches Pandas pct_change: {matches}")

    print("\n" + "=" * 70)
    print("2) Manual 20-day rolling mean vs Pandas .rolling().mean()")
    print("=" * 70)
    manual_roll = manual_rolling_mean(aapl["close"].values, window=20)
    pandas_roll = aapl["close"].rolling(20).mean().values
    matches_roll = np.allclose(manual_roll[19:], pandas_roll[19:])
    print(f"Manual NumPy result matches Pandas rolling mean: {matches_roll}")

    print("\n" + "=" * 70)
    print("3) Correlation matrix across all tickers (daily returns)")
    print("=" * 70)
    corr = correlation_matrix(df)
    print(corr.round(2))

    print("\n" + "=" * 70)
    print("4) Monte Carlo: simulate 30-day price paths for AAPL")
    print("=" * 70)
    hist_returns = aapl["daily_return"].dropna()
    paths = monte_carlo_price_paths(
        start_price=aapl["close"].iloc[-1],
        daily_mean=hist_returns.mean(),
        daily_std=hist_returns.std(),
        days=30,
        simulations=1000,
    )
    final_prices = paths[:, -1]
    print(f"Starting price: {aapl['close'].iloc[-1]:.2f}")
    print(f"Simulated price after 30 days -- mean: {final_prices.mean():.2f}, "
          f"5th pct: {np.percentile(final_prices, 5):.2f}, "
          f"95th pct: {np.percentile(final_prices, 95):.2f}")
