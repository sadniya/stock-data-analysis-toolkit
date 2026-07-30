# Stock Data Analysis Toolkit

A hands-on project using only **Python, NumPy, Pandas, and SQL** — no pipelines,
no scheduling, no deployment. Built to stretch what you already know.

## Setup

```bash
pip install yfinance pandas numpy
```

(SQLite comes built into Python — no server or install needed.)

## Run order

```bash
python 01_fetch_and_clean.py     # downloads data, cleans it, saves prices_clean.csv
python 02_load_to_sql.py         # loads the CSV into stocks.db (SQLite)
python 03_sql_vs_pandas.py       # answers 4 questions in SQL AND Pandas -- compare them
python 04_numpy_exercises.py     # rebuilds pandas calcs in raw NumPy + Monte Carlo sim
```

Each script prints its output to the terminal — no dashboard needed. Read the
printed results and the code side by side.

## What each step teaches

| Script | Focus | Key skill |
|---|---|---|
| `01_fetch_and_clean.py` | Pandas | cleaning, reshaping, groupby transforms |
| `02_load_to_sql.py` | SQL | schema basics, indexing, `to_sql()` |
| `03_sql_vs_pandas.py` | SQL ↔ Pandas | window functions, `LAG()`/`shift()`, `RANK()` |
| `04_numpy_exercises.py` | NumPy | vectorization from scratch, Monte Carlo simulation |

## How to actually get value from this (not just run it)

1. **Before running `03`, guess the answer yourself.** Which stock do you *think*
   had the highest average return? Then check if you're right.
2. **Read the SQL and Pandas code side by side** for each question. Notice: a SQL
   `GROUP BY` + `AVG()` is a Pandas `.groupby().mean()`. A SQL `LAG()` is a Pandas
   `.shift()`. This mapping is the single most interview-relevant skill here.
3. **In `04`, don't skip to running it — try writing `manual_rolling_mean` yourself
   first**, then compare to the provided version. Getting it wrong first is where
   the learning happens.
4. **Break things on purpose.** Change `WHERE rnk <= 5` to `<= 1`. Change the
   Monte Carlo `simulations` count from 1000 to 10 and see the percentiles get
   noisier. Small experiments build intuition faster than reading.

## Extending it (optional, once the above feels easy)

- Add a 5th comparison question of your own (e.g., "average volume by ticker per month")
- Try a different rolling window (5-day vs 20-day) and see how correlation changes
- Swap in a different stock basket (e.g., all one sector) and see if correlations rise
