import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="GoldSense AI Live Monitor", page_icon="📈", layout="wide"
)

from streamlit_autorefresh import st_autorefresh

# Run every 10 seconds (10000 milliseconds)
count = st_autorefresh(interval=10000, limit=None, key="datarefresh")

@st.cache_resource
def init_connection():
  url = st.secrets["SUPABASE_URL"]
  key = st.secrets["SUPABASE_KEY"]
  return create_client(url, key)


supabase = init_connection()

st.title("GoldSense AI - XAUUSD Scalping Monitor")
st.markdown("Real-time telemetry from your local MT5 trading engine.")

# Fetch latest metrics from Supabase
response = (
    supabase.table("trading_metrics")
    .select("*")
    .order("id", desc=True)
    .limit(20)
    .execute()
)
df = pd.DataFrame(response.data)

if not df.empty:
  latest = df.iloc[0]

  col1, col2, col3 = st.columns(3)
  col1.metric("Live Equity", f"${latest['equity']:,.2f}")
  col2.metric("Balance", f"${latest['balance']:,.2f}")
  col3.metric("Open Trades", int(latest["open_trades"]))

  st.markdown("**Latest Status Message**")
  st.info(latest["status_message"])

  st.markdown("**Performance History**")
  st.dataframe(df, use_container_width=True)

  st.markdown("**Equity Curve**")
  st.line_chart(df.set_index("timestamp")["equity"])
else:
  st.warning("No telemetry data found. Waiting for local engine transmission...")