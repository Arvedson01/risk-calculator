st.cache_data.clear()

import streamlit as st
from PIL import Image

# Page setup
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")

# Load and display logo
logo = Image.open("logo.png")
st.image(logo, width=150)

# App title
st.title("📊 1% Risk Management Calculator")

# --- User Inputs ---
account_balance = st.number_input("Account Balance (SEK)", min_value=0.0, value=10000.0)
risk_percent = st.number_input("Risk % per trade", min_value=0.1, max_value=100.0, value=1.0)
entry_price = st.number_input("Entry Price (SEK)", min_value=0.01, value=100.0)
stop_loss_price = st.number_input("Stop Loss Price (SEK)", min_value=0.01, value=95.0)
target_price = st.number_input("Target Price (SEK)", min_value=0.01, value=120.0)
leverage = st.number_input("Leverage (e.g. 5× = 5)", min_value=1.0, max_value=100.0, value=1.0)

# --- Core Calculations ---
risk_amount = account_balance * (risk_percent / 100)
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit
reward_per_unit = abs(target_price - entry_price)
reward_risk_ratio = reward_per_unit / risk_per_unit
total_trade_cost = (position_size * entry_price) / leverage

# --- Results Display ---
st.subheader("📈 Trade Summary")
st.write("Leverage: ", leverage, "×")
st.write("Max Risk Amount: ", round(risk_amount, 2), "SEK")
st.write("Suggested Position Size: ", int(position_size), "units")
st.write("Estimated Trade Cost (with leverage): ", round(total_trade_cost, 2), "SEK")
st.write("Reward-to-Risk Ratio: ", round(reward_risk_ratio, 2))

# --- Warnings ---
if reward_risk_ratio < 2:
    st.warning("⚠️ Reward-to-risk ratio is below 2:1")

if total_trade_cost > account_balance:
    st.warning("⚠️ Trade size exceeds your available capital")

# --- Disclaimer ---
st.markdown("---")
st.caption("📘 This tool is for educational purposes only. Trade at your own risk.")
