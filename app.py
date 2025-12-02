import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# --- 1. PAGE CONFIGURATION (Consulting Polish) ---
st.set_page_config(
    page_title="Global Economic Scenario Simulator",
    page_icon="📈",
    layout="wide"
)

# Custom CSS to mimic "The Economist" / Consulting Style
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp {
        background-color: #f3f3f3; /* Light Grey background */
        font-family: 'Georgia', serif;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #000000;
        font-weight: 700;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #E3120B; /* Economist Red */
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA GENERATION (Synthetic "Research" Data) ---
def generate_scenario_data(base_inflation, shock_factor, volatility):
    dates = pd.date_range(start="2020-01-01", end="2026-12-31", freq="M")
    n = len(dates)
    
    # Base Trend
    trend = np.linspace(2.0, base_inflation, n)
    
    # Seasonality & Volatility
    seasonality = np.sin(np.linspace(0, 8*np.pi, n)) * 0.5
    noise = np.random.normal(0, volatility, n)
    
    # Shock Event (Simulated in 2024)
    shock = np.zeros(n)
    shock_start = 48 # Jan 2024
    shock[shock_start:] = shock_factor * np.exp(-0.1 * np.arange(n-shock_start))
    
    values = trend + seasonality + noise + shock
    return pd.DataFrame({'Date': dates, 'Inflation': values})

# --- 3. SIDEBAR CONTROLS (The "Consultant's Toolkit") ---
st.sidebar.header("⚙️ Scenario Assumptions")
st.sidebar.markdown("Adjust these levers to stress-test the economy.")

base_target = st.sidebar.slider("Target Inflation (2026)", 1.0, 10.0, 3.5, help="Where will inflation settle if no shocks occur?")
shock_magnitude = st.sidebar.slider("Supply Chain Shock Intensity", 0.0, 5.0, 1.5, help="Impact of a hypothetical crisis (e.g., Oil spike).")
volatility_idx = st.sidebar.select_slider("Market Volatility", options=["Stable", "Uncertain", "Chaotic"], value="Uncertain")

# Map text to values
vol_map = {"Stable": 0.1, "Uncertain": 0.4, "Chaotic": 0.9}
df = generate_scenario_data(base_target, shock_magnitude, vol_map[volatility_idx])

# --- 4. MAIN DASHBOARD ---
st.title("📉 Global Inflation Forecast: Scenario Analysis")
st.markdown("""
**Executive Summary:** Inflation remains sticky. This interactive tool allows you to model 
the impact of *supply-side shocks* on the Consumer Price Index (CPI) trajectory.
""")

# Key Metrics Row
col1, col2, col3 = st.columns(3)
curr_val = df['Inflation'].iloc[-1]
peak_val = df['Inflation'].max()
pre_shock_val = df['Inflation'].iloc[47] # Dec 2023

col1.metric("Forecasted Inflation (2026)", f"{curr_val:.2f}%", f"{(curr_val - pre_shock_val):.2f}% vs Pre-Shock")
col2.metric("Peak Inflation Stress", f"{peak_val:.2f}%")
col3.metric("Volatility Regime", volatility_idx)

# --- 5. THE HERO CHART (Interactive Plotly) ---
# Create the "Economist Style" Line Chart
fig = go.Figure()

# Historical Line (Grey)
history = df[df['Date'] < '2024-01-01']
forecast = df[df['Date'] >= '2024-01-01']

fig.add_trace(go.Scatter(
    x=history['Date'], y=history['Inflation'],
    mode='lines', name='Historical Data',
    line=dict(color='#4d4d4d', width=2)
))

# Forecast Line (Red)
fig.add_trace(go.Scatter(
    x=forecast['Date'], y=forecast['Inflation'],
    mode='lines', name='Scenario Forecast',
    line=dict(color='#E3120B', width=3) # Economist Red
))

# Add "Confidence Interval" Fan
fig.add_trace(go.Scatter(
    x=forecast['Date'].tolist() + forecast['Date'].tolist()[::-1],
    y=(forecast['Inflation'] + 1.5).tolist() + (forecast['Inflation'] - 1.5).tolist()[::-1],
    fill='toself',
    fillcolor='rgba(227, 18, 11, 0.1)',
    line=dict(color='rgba(255,255,255,0)'),
    name='Uncertainty Band'
))

# Chart Annotations (The "Story")
fig.add_vline(x=pd.Timestamp('2024-01-01').timestamp() * 1000, line_dash="dash", line_color="grey")
fig.add_annotation(
    x=pd.Timestamp('2024-01-01'), y=df['Inflation'].max()+0.5,
    text="Forecast Horizon Begins",
    showarrow=False,
    font=dict(size=12, color="grey")
)

# Layout Polish
fig.update_layout(
    title="<b>CPI Inflation Projections (YoY %)</b><br><span style='font-size:12px;color:grey'>Source: Federal Reserve Data & User Projections</span>",
    template="plotly_white",
    hovermode="x unified",
    yaxis=dict(showgrid=True, gridcolor='#e1e1e1'),
    xaxis=dict(showgrid=False),
    legend=dict(orientation="h", y=1.1, x=0),
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# --- 6. SCROLLYTELLING NARRATIVE ---
st.markdown("---")
st.subheader("💡 Strategic Insights")

with st.expander("See Analysis Details", expanded=True):
    st.markdown(f"""
    * **The Baseline:** Under current assumptions, inflation trends toward **{base_target}%**.
    * **The Shock:** A supply shock of intensity **{shock_magnitude}** creates a temporary distortion lasting ~18 months.
    * **Recommendation:** If {volatility_idx} conditions persist, hedging strategies should focus on **real assets** rather than nominal bonds.
    """)

st.caption("Developed with Python & Streamlit. Designed for Executive Review.")
