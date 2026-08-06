import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Stock Data Analysis Dashboard", layout="wide")

st.title("📈 Stock Data Analysis Dashboard")
st.markdown("An interactive web application to analyze stock prices, correlate returns, and run Monte Carlo simulations.")

# Database and CSV paths
DB_PATH = "stocks.db"
CSV_PATH = "prices_clean.csv"

# Load data helpers
@st.cache_data
def load_data_from_csv():
    df = pd.read_csv(CSV_PATH, parse_dates=["date"])
    return df

@st.cache_data
def load_tickers_from_db():
    conn = sqlite3.connect(DB_PATH)
    tickers = pd.read_sql("SELECT DISTINCT ticker FROM daily_prices", conn)["ticker"].tolist()
    conn.close()
    return tickers

# Check if data exists and load it
try:
    df = load_data_from_csv()
    tickers = load_tickers_from_db()
except Exception as e:
    st.error(f"Error loading database or CSV file: {e}. Please ensure steps 1 and 2 are run successfully.")
    st.stop()

# Sidebar inputs
st.sidebar.header("Dashboard Controls")
selected_ticker = st.sidebar.selectbox("Select Ticker", tickers)
rolling_window = st.sidebar.slider("Rolling Mean Window (Days)", min_value=5, max_value=100, value=20)

st.sidebar.markdown("---")
st.sidebar.header("Monte Carlo Parameters")
num_sims = st.sidebar.slider("Number of Simulations", min_value=50, max_value=2000, value=500, step=50)
forecast_days = st.sidebar.slider("Forecast Days", min_value=10, max_value=120, value=30)

# Main tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Price & Technicals", "🔗 Correlation Analysis", "🎲 Monte Carlo Simulation"])

# TAB 1: Price and Technical Indicators
with tab1:
    st.subheader(f"{selected_ticker} Price Trends")
    ticker_df = df[df["ticker"] == selected_ticker].sort_values("date").copy()
    
    # Calculate rolling mean
    ticker_df["rolling_mean"] = ticker_df["close"].rolling(rolling_window).mean()
    
    # Render interactive line chart
    chart_df = ticker_df.set_index("date")[["close", "rolling_mean"]]
    st.line_chart(chart_df)
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"${ticker_df['close'].iloc[-1]:.2f}")
    col2.metric("Average Daily Return", f"{ticker_df['daily_return'].mean()*100:.3f}%")
    col3.metric("Volatility (Std Dev)", f"{ticker_df['daily_return'].std()*100:.3f}%")

# TAB 2: Correlation Matrix Heatmap
with tab2:
    st.subheader("Ticker Correlation Matrix")
    st.markdown("Showing how stock daily returns move together (1.0 = perfect positive correlation).")
    
    wide_df = df.pivot(index="date", columns="ticker", values="daily_return").dropna()
    corr_matrix = wide_df.corr()
    
    # Plot using seaborn
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    st.pyplot(fig)

# TAB 3: Monte Carlo Simulation Path Plots
with tab3:
    st.subheader(f"Monte Carlo Simulation for {selected_ticker}")
    st.markdown(f"Simulating {num_sims} paths for the next {forecast_days} trading days using historical volatility.")
    
    hist_returns = ticker_df["daily_return"].dropna()
    mean = hist_returns.mean()
    std = hist_returns.std()
    start_price = ticker_df["close"].iloc[-1]
    
    # Monte Carlo simulation logic
    rng = np.random.default_rng(42)
    random_returns = rng.normal(loc=mean, scale=std, size=(num_sims, forecast_days))
    growth_factors = 1 + random_returns
    cumulative_growth = np.cumprod(growth_factors, axis=1)
    price_paths = start_price * cumulative_growth
    
    # Plotting paths
    fig, ax = plt.subplots(figsize=(10, 5))
    for i in range(min(num_sims, 100)):  # Plot up to 100 paths for clean UI
        ax.plot(price_paths[i, :], color="blue", alpha=0.08)
        
    # Calculate forecast percentiles
    p5 = np.percentile(price_paths[:, -1], 5)
    p50 = np.percentile(price_paths[:, -1], 50)
    p95 = np.percentile(price_paths[:, -1], 95)
    
    ax.axhline(start_price, color="black", linestyle="--", label=f"Start Price (${start_price:.2f})")
    ax.axhline(p50, color="green", linestyle="-", label=f"Median Forecast (${p50:.2f})")
    ax.axhline(p5, color="red", linestyle=":", label=f"5th Percentile (${p5:.2f})")
    ax.axhline(p95, color="purple", linestyle=":", label=f"95th Percentile (${p95:.2f})")
    ax.set_title(f"{selected_ticker} Monte Carlo Forecast Paths")
    ax.set_ylabel("Stock Price ($)")
    ax.set_xlabel("Days Ahead")
    ax.legend()
    
    st.pyplot(fig)
    
    # Calculate probability of making a profit
    prob_gain = (price_paths[:, -1] > start_price).mean() * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Median Forecasted Price", f"${p50:.2f}")
    col2.metric("Probability of Gain", f"{prob_gain:.1f}%")
