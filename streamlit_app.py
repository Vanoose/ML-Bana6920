import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page setup ---
st.set_page_config(page_title="Portfolio Risk Dashboard", layout="wide")
st.title("Portfolio Risk and Performance Dashboard")

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_csv("stock_macro_risk_score_with_beta_sharpe.csv", parse_dates=["Date"])
    return df

df = load_data()

# --- Sidebar: select ticker ---
st.sidebar.header("Filter")
tickers = df["Ticker"].unique().tolist()
selected_ticker = st.sidebar.selectbox("Select Ticker", tickers)

df_filtered = df[df["Ticker"] == selected_ticker]

# --- Portfolio weights (equal-weight sample) ---
sample_weights = df.groupby("Ticker")["Adj Close"].last()
sample_weights = sample_weights / sample_weights.sum()

# --- Alert if high risk score ---
high_risk = df_filtered[df_filtered["RiskScore"] > 70]
if not high_risk.empty:
    st.error(f"Risk Alert: {len(high_risk)} days where {selected_ticker} RiskScore exceeded 70!")

# --- Metrics ---
latest = df_filtered.sort_values("Date").iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Risk Score", f"{latest['RiskScore']:.1f}")
col2.metric("Beta", f"{latest['Beta']:.2f}")
col3.metric("Sharpe Ratio", f"{latest['SharpeRatio']:.2f}")

st.markdown("---")

# --- Charts in tabs ---
tab1, tab2, tab3 = st.tabs(["Risk Score Trend", "Beta Trend", "Sharpe Ratio Trend"])

with tab1:
    fig1 = px.line(df_filtered, x="Date", y="RiskScore", title=f"{selected_ticker} Risk Score Over Time")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.line(df_filtered, x="Date", y="Beta", title=f"{selected_ticker} Beta Over Time")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = px.line(df_filtered, x="Date", y="SharpeRatio", title=f"{selected_ticker} Sharpe Ratio Over Time")
    st.plotly_chart(fig3, use_container_width=True)

# --- Portfolio Composition ---
st.markdown("## Portfolio Composition")

# Pie chart
fig_pie = px.pie(names=sample_weights.index, values=sample_weights.values,
                 title="Sample Portfolio Allocation", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# Treemap
fig_tree = px.treemap(
    names=sample_weights.index,
    parents=[""] * len(sample_weights),
    values=sample_weights.values,
    title="Portfolio Allocation Treemap"
)
st.plotly_chart(fig_tree, use_container_width=True)

# --- Data Table ---
with st.expander("View Raw Data"):
    st.dataframe(df_filtered.tail(100))
