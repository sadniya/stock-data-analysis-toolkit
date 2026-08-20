import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Stock Data Analysis Toolkit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)

# Custom CSS for a complete layout redesign (hides sidebar, implements top control bar, uses massive fonts, and a premium Nordic Blue theme)
st.markdown("""
<style>
    /* Import modern Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    /* Global Styles and Large Font Sizes */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #f1f5f9; /* Nordic slate-blue background */
        color: #0f172a;
        font-size: 20px !important; /* Large, highly readable text */
    }
    
    /* Hide the Streamlit sidebar completely */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    .st-emotion-cache-1dp543d {
        padding: 4rem 1rem 1rem !important;
    }

    /* Premium Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); /* Deep Navy to Electric Blue */
        border-radius: 16px;
        padding: 45px 50px;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.12);
        margin-bottom: 25px;
    }
    .header-banner h1 {
        font-family: 'Space Grotesk', sans-serif !important;
        margin: 0; 
        color: #ffffff !important; 
        font-weight: 800 !important;
        font-size: 46px !important; /* Huge Header */
        letter-spacing: -1px;
    }
    .header-banner p {
        margin: 12px 0 0 0; 
        color: #e2e8f0; 
        font-size: 22px !important; /* Large subtitle */
        font-weight: 400;
    }
    
    /* Control Center Card (Replaces the Sidebar) */
    .control-panel {
        background: #ffffff;
        border-radius: 16px;
        padding: 30px 40px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
        margin-bottom: 30px;
    }
    .control-panel-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 22px !important;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 20px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
    }
    
    /* Styled widgets labels inside controls */
    div[data-testid="stWidgetLabel"] p {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #334155 !important;
    }
    
    /* Premium Large Metric Cards */
    .metric-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 28px 32px; /* Generous padding */
        border: 1px solid #e2e8f0;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.03);
        text-align: left;
        margin-bottom: 15px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 32px rgba(30, 58, 138, 0.08);
        border-color: #2563eb;
    }
    .metric-title {
        font-size: 15px !important;
        color: #64748b;
        margin-bottom: 8px;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 36px !important; /* Extra large numbers */
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -1px;
    }
    .metric-delta {
        font-size: 17px !important; /* Larger changes info */
        font-weight: 700;
        margin-top: 8px;
        display: flex;
        align-items: center;
    }
    .delta-positive {
        color: #15803d;
    }
    .delta-negative {
        color: #b91c1c;
    }
    
    /* Large custom section headers */
    .section-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 800 !important;
        font-size: 30px !important; /* Huge titles */
        color: #1e3a8a !important;
        margin-top: 30px !important;
        margin-bottom: 20px !important;
        border-bottom: 4px solid #3b82f6;
        padding-bottom: 8px;
        display: inline-block;
    }
    
    /* Card box for chart groups */
    .chart-container {
        background: #ffffff;
        border-radius: 16px;
        padding: 30px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.02);
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# Database and CSV paths
DB_PATH = "stocks.db"
CSV_PATH = "prices_clean.csv"

# Load data helper with caching
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

# Header Banner
st.markdown("""
<div class="header-banner">
    <h1>📈 Quantitative Analytics Terminal</h1>
    <p>A professional financial dashboard integrating SQLite indexing, Pandas analytics, and Monte Carlo NumPy projections.</p>
</div>
""", unsafe_allow_html=True)

# ----------------- NEW HORIZONTAL CONTROL CENTER (No Sidebar) -----------------
st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
st.markdown("<div class='control-panel-title'>🎛️ Terminal Configuration Control</div>", unsafe_allow_html=True)

ccol1, ccol2, ccol3 = st.columns([1, 1.2, 1.2])

with ccol1:
    selected_ticker = st.selectbox("Selected Ticker Symbol", tickers)

with ccol2:
    # Use columns inside for cleaner look
    scol1, scol2 = st.columns(2)
    with scol1:
        short_window = st.number_input("Short Window (Days)", min_value=5, max_value=30, value=20)
    with scol2:
        long_window = st.number_input("Long Window (Days)", min_value=31, max_value=100, value=50)

with ccol3:
    mcol1, mcol2 = st.columns(2)
    with mcol1:
        num_sims = st.number_input("Forecast Paths", min_value=50, max_value=1500, value=500, step=50)
    with mcol2:
        forecast_days = st.number_input("Forecast Days", min_value=10, max_value=120, value=30)

st.markdown("</div>", unsafe_allow_html=True)

# Load Ticker Data
ticker_df = df[df["ticker"] == selected_ticker].sort_values("date").copy()

# Calculate indicators
ticker_df["short_sma"] = ticker_df["close"].rolling(short_window).mean()
ticker_df["long_sma"] = ticker_df["close"].rolling(long_window).mean()

# Financial metrics calculations
current_price = ticker_df['close'].iloc[-1]
pct_change_all = ((current_price - ticker_df['close'].iloc[0]) / ticker_df['close'].iloc[0]) * 100
daily_returns = ticker_df['daily_return'].dropna()
avg_daily_return = daily_returns.mean() * 100
annualized_vol = daily_returns.std() * np.sqrt(252) * 100

# Crossover Signals
last_short = ticker_df["short_sma"].iloc[-1]
last_long = ticker_df["long_sma"].iloc[-1]

signal = "NEUTRAL"
signal_color = "#64748b"
if last_short > last_long:
    signal = "BUY (Bullish Crossover)"
    signal_color = "#15803d"
elif last_short < last_long:
    signal = "SELL (Bearish Crossover)"
    signal_color = "#b91c1c"

# Display KPI Metric Cards with LARGE Fonts
kcol1, kcol2, kcol3, kcol4 = st.columns(4)

kcol1.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Last Close Price</div>
    <div class="metric-value">${current_price:.2f}</div>
    <div class="metric-delta delta-positive">● Data Active</div>
</div>
""", unsafe_allow_html=True)

delta_class = "delta-positive" if pct_change_all >= 0 else "delta-negative"
sign = "+" if pct_change_all >= 0 else ""
kcol2.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Period Performance</div>
    <div class="metric-value">{sign}{pct_change_all:.2f}%</div>
    <div class="metric-delta {delta_class}">Cumulative Return</div>
</div>
""", unsafe_allow_html=True)

kcol3.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Annualized Volatility</div>
    <div class="metric-value">{annualized_vol:.2f}%</div>
    <div class="metric-delta" style="color: #b45309;">Asset Volatility</div>
</div>
""", unsafe_allow_html=True)

kcol4.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Crossover Signal</div>
    <div class="metric-value" style="color: {signal_color}; font-size: 22px; font-weight: 800; padding-top: 5px;">{signal}</div>
    <div class="metric-delta" style="color: #64748b;">SMA {short_window} / {long_window}</div>
</div>
""", unsafe_allow_html=True)

# ----------------- SIDE-BY-SIDE ANALYTICS GRID -----------------
st.markdown("<br>", unsafe_allow_html=True)
col_left, col_right = st.columns([1.3, 1])

# LEFT COLUMN: Price Terminal and Correlation Matrix
with col_left:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📈 Market Execution & Moving Averages</div>", unsafe_allow_html=True)
    
    # Plotly Interactive Price Chart
    fig_price = go.Figure()
    fig_price.add_trace(go.Candlestick(
        x=ticker_df['date'],
        open=ticker_df['open'],
        high=ticker_df['high'],
        low=ticker_df['low'],
        close=ticker_df['close'],
        name="Market Price"
    ))
    fig_price.add_trace(go.Scatter(
        x=ticker_df['date'],
        y=ticker_df['short_sma'],
        line=dict(color='#ea580c', width=2),
        name=f'{short_window}-day SMA'
    ))
    fig_price.add_trace(go.Scatter(
        x=ticker_df['date'],
        y=ticker_df['long_sma'],
        line=dict(color='#0969da', width=2),
        name=f'{long_window}-day SMA'
    ))
    
    fig_price.update_layout(
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False,
        yaxis_title="Price ($)",
        height=450,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor="#eaeef2"),
        yaxis=dict(gridcolor="#eaeef2")
    )
    st.plotly_chart(fig_price, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Correlation Matrix Section
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔗 Inter-Asset Return Correlations</div>", unsafe_allow_html=True)
    wide_df = df.pivot(index="date", columns="ticker", values="daily_return").dropna()
    corr_matrix = wide_df.corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu",
        zmin=-1.0, zmax=1.0,
        labels=dict(x="Asset", y="Asset", color="Correlation")
    )
    fig_corr.update_layout(
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=430,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# RIGHT COLUMN: Monte Carlo & Scatter Study
with col_right:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🎲 Monte Carlo Asset Forecasting</div>", unsafe_allow_html=True)
    
    # MC Logic
    mean_ret = daily_returns.mean()
    std_ret = daily_returns.std()
    
    rng = np.random.default_rng(42)
    random_returns = rng.normal(loc=mean_ret, scale=std_ret, size=(num_sims, forecast_days))
    growth_factors = 1 + random_returns
    cumulative_growth = np.cumprod(growth_factors, axis=1)
    price_paths = current_price * cumulative_growth
    
    # Calculate quantiles over paths
    p5 = np.percentile(price_paths[:, -1], 5)
    p50 = np.percentile(price_paths[:, -1], 50)
    p95 = np.percentile(price_paths[:, -1], 95)
    prob_gain = (price_paths[:, -1] > current_price).mean() * 100
    
    # Plot forecast paths
    fig_mc = go.Figure()
    days_array = np.arange(1, forecast_days + 1)
    for i in range(min(num_sims, 80)):
        fig_mc.add_trace(go.Scatter(
            x=days_array,
            y=price_paths[i, :],
            mode='lines',
            line=dict(width=1, color='rgba(9, 105, 218, 0.08)'),
            showlegend=False
        ))
        
    fig_mc.add_trace(go.Scatter(
        x=days_array, y=np.percentile(price_paths, 50, axis=0),
        line=dict(color='#1a7f37', width=3),
        name="Median Path (50th Pct)"
    ))
    fig_mc.add_trace(go.Scatter(
        x=days_array, y=np.percentile(price_paths, 95, axis=0),
        line=dict(color='#8250df', width=2, dash='dash'),
        name="Optimistic Path"
    ))
    fig_mc.add_trace(go.Scatter(
        x=days_array, y=np.percentile(price_paths, 5, axis=0),
        line=dict(color='#cf222e', width=2, dash='dash'),
        name="Pessimistic Path"
    ))
    
    fig_mc.update_layout(
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Days Forecasted",
        yaxis_title="Stock Price ($)",
        height=350,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_mc, use_container_width=True)
    
    # Stats row
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.markdown(f"""
    <div class="metric-card" style="padding: 15px 20px;">
        <div class="metric-title" style="font-size: 12px !important;">Start Price</div>
        <div class="metric-value" style="font-size: 22px !important;">${current_price:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    mcol2.markdown(f"""
    <div class="metric-card" style="padding: 15px 20px;">
        <div class="metric-title" style="font-size: 12px !important;">Median Forecast</div>
        <div class="metric-value" style="font-size: 22px !important; color:#1a7f37;">${p50:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    mcol3.markdown(f"""
    <div class="metric-card" style="padding: 15px 20px;">
        <div class="metric-title" style="font-size: 12px !important;">Gain Prob.</div>
        <div class="metric-value" style="font-size: 22px !important; color:#1a7f37;">{prob_gain:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Scatter study
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔗 Dual Asset Regression Study</div>", unsafe_allow_html=True)
    comp_ticker = st.selectbox("Select Asset to Compare With", [t for t in tickers if t != selected_ticker])
    
    # Join daily returns
    scatter_data = wide_df[[selected_ticker, comp_ticker]].reset_index()
    
    fig_scatter = px.scatter(
        scatter_data,
        x=selected_ticker,
        y=comp_ticker,
        trendline="ols",
        trendline_color_override="#d97706",
        labels={selected_ticker: f"{selected_ticker} Daily Return", comp_ticker: f"{comp_ticker} Daily Return"}
    )
    fig_scatter.update_layout(
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
