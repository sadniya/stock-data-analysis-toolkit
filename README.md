# Stock Data Analysis Toolkit

A simple project using Python, Pandas, NumPy, and SQL to learn and compare data manipulation approaches. No complex pipelines or deployment needed.

## Setup
```bash
pip install yfinance pandas numpy
```
Note: SQLite comes built-in with Python, so there's no need to install a database server.

## Run Order & How it Works
1. **01_fetch_and_clean.py**: Downloads raw stock data using `yfinance`, cleans it (removes duplicates, handles missing values), calculates daily returns, and saves the output to `prices_clean.csv`.
2. **02_load_to_sql.py**: Loads the clean CSV into a local SQLite database (`stocks.db`) and sets up a composite index to keep queries fast.
3. **03_sql_vs_pandas.py**: Solves the same analytical questions in both SQL and Pandas to show how the syntax and logic compare side-by-side.
4. **04_numpy_exercises.py**: Re-implements Pandas operations using raw NumPy arrays, and runs a Monte Carlo simulation.

## Progress
- [x] Step 1: Download & clean stock data (saved to `prices_clean.csv`)
- [x] Step 2: Load clean data to SQLite database (`stocks.db`)
- [x] Step 3: Compare queries in SQL vs Pandas
- [x] Step 4: Run NumPy exercises & Monte Carlo simulation