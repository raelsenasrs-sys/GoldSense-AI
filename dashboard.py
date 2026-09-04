import streamlit as st
import pandas as pd
import json
import os

# Page Configuration
st.set_page_config(page_title="GoldSense AI Command Center", page_icon="⚡", layout="wide")

st.title("⚡ GoldSense AI: XAUUSD Scalping Command Center")
st.markdown("Real-time monitoring of automated trade execution, risk parameters, and self-learning memory.")

# Load Memory Database
MEMORY_FILE = "goldsense_memory.json"

def load_data():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

data = load_data()

if not data:
    st.warning("No trade records or memory logs found yet. Run your main autonomous script to generate data.")
else:
    # Flatten JSON data for Pandas
    records = []
    for item in data:
        flat_item = {**item.get("features", {}), **item.get("result", {})}
        records.append(flat_item)
    
    df = pd.DataFrame(records)

    # Top-Level Metrics Overview
    st.markdown("### **Key Performance Indicators**")
    col1, col2, col3, col4 = st.columns(4)
    
    total_trades = len(df)
    win_rate = (df['success'].sum() / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = df['pnl'].sum() if 'pnl' in df.columns else 0
    avg_r = df['return_r'].mean() if 'return_r' in df.columns else 0

    col1.metric("Total Executed Trades", total_trades)
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Net Realized PnL", f"${total_pnl:.2f}")
    col4.metric("Average R-Multiple", f"{avg_r:.2f}R")

    # Visualizations / Analytics
    st.markdown("---")
    st.markdown("### **Performance & Equity Curve**")
    if 'pnl' in df.columns:
        df['cumulative_pnl'] = df['pnl'].cumsum()
        st.line_chart(df['cumulative_pnl'])

    # Detailed Trade History Ledger
    st.markdown("---")
    st.markdown("### **Executed Trade Audit Trail**")
    st.dataframe(df, use_container_width=True)

    # Self-Learner Adaptation Status
    st.markdown("---")
    st.markdown("### **AI Self-Learning Status**")
    st.info("System is actively recording market volatility, phase types, and session parameters to dynamically adjust execution filters.")