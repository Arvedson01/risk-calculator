import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd

# 🧱 Page setup
st.set_page_config(page_title="📊 Risk Calculator", page_icon="📈")

# 🖼️ Logo
logo = Image.open("logo.png")
st.image(logo, width=150)

# 🧭 App title
st.title("📊 1% Risk Management Calculator")

# 📥 User Inputs
account_balance = st.number_input("Account Balance", min_value=0.0, value=10000.0)
risk_percent = st.number_input("Risk % per trade", min_value=0.0, value=1.0)
entry_price = st.number_input("Entry Price", min_value=0.0, value=100.0)
stop_loss_price = st.number_input("Stop Loss Price", min_value=0.0, value=95.0)
target_price = st.number_input("Target Price", min_value=0.0, value=120.0)
leverage = st.number_input("Leverage (e.g. 1x, 2x, 3x)", min_value=1.0, value=1.0)

# 🧮 Core Calculations
risk_amount = account_balance * (risk_percent / 100)
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit
total_trade_cost = position_size * entry_price / leverage
reward_per_unit = abs(target_price - entry_price)
reward_to_risk = reward_per_unit / risk_per_unit

# 📊 Styled Table Display (Dark-themed)
st.subheader("📋 Trade Summary")

summary_df = pd.DataFrame({
    "Metric": [
        "Risk Amount",
        "Risk per Unit",
        "Suggested Position Size",
        "Total Trade Cost (with Leverage)",
        "Reward-to-Risk Ratio"
    ],
    "Value": [
        f"{risk_amount:,.2f}",
        f"{risk_per_unit:,.2f}",
        f"{position_size:,.2f} units",
        f"{total_trade_cost:,.2f}",
        f"{reward_to_risk:.2f} : 1"
    ]
})

st.dataframe(summary_df.style.set_properties(**{
    'background-color': '#0e1117',
    'color': '#fafafa',
    'border-color': '#444'
}), height=210)

# 📈 Chart Visualization
st.subheader("📈 Trade Visualization")

fig, ax = plt.subplots(figsize=(6, 4))

# Highlight zones
ax.axhspan(stop_loss_price, entry_price, color='red', alpha=0.2, label='Risk')
ax.axhspan(entry_price, target_price, color='green', alpha=0.2, label='Reward')

# Price lines
ax.axhline(stop_loss_price, color='red', linestyle='--', label=f'Stop Loss ({stop_loss_price})')
ax.axhline(entry_price, color='orange', linestyle='--', label=f'Entry ({entry_price})')
ax.axhline(target_price, color='green', linestyle='--', label=f'Target ({target_price})')

ax.set_xlabel("Trade Setup")
ax.set_ylabel("Price")
ax.set_title("Price Zones")
ax.legend()
st.pyplot(fig)

# ⚠️ Warnings
if reward_to_risk < 2:
    st.warning("⚠️ Warning: Reward-to-risk ratio is below 2:1")

if total_trade_cost > account_balance:
    st.error("🚫 Warning: This trade exceeds your available capital")

# 📘 Disclaimer
st.markdown("---")
st.markdown("📌 **Disclaimer:** This tool is for educational purposes only and does not constitute financial advice.")
st.markdown("💡 Always consult with a certified financial professional before making trading decisions.")
