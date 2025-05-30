import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd

# ─── Page Setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")

# ─── Logo ──────────────────────────────────────────────────────────────────────
logo = Image.open("logo.png")
st.image(logo, width=150)

# ─── App Title ────────────────────────────────────────────────────────────────
st.title("📊 1% Risk Management Calculator")

# ─── User Inputs ───────────────────────────────────────────────────────────────
account_balance = st.number_input("💰 Account Balance", min_value=0.0, value=10000.0)
risk_percent = st.number_input("⚠️ Risk % per trade", min_value=0.0, max_value=100.0, value=1.0)
entry_price = st.number_input("📥 Entry Price", min_value=0.0, value=100.0)
stop_loss_price = st.number_input("🛑 Stop Loss", min_value=0.0, value=95.0)
target_price = st.number_input("🎯 Target Price", min_value=0.0, value=120.0)
leverage = st.number_input("🧮 Leverage [e.g. 1x, 2x, 5x]", min_value=1.0, max_value=100.0, value=1.0)

# ─── Core Calculations ─────────────────────────────────────────────────────────
risk_amount = account_balance * (risk_percent / 100)
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit
total_trade_cost = position_size * entry_price / leverage
reward_per_unit = abs(target_price - entry_price)
reward_risk_ratio = reward_per_unit / risk_per_unit

# ─── Trade Summary Table ───────────────────────────────────────────────────────
st.subheader("📋 Trade Summary")

summary_data = {
    "Metric": ["Account Size", "Max Risk", "Entry Price", "Stop Loss", "Target Price", "Position Size", "Total Trade Cost", "Reward:Risk Ratio"],
    "Value": [f"{account_balance:,.2f}", f"{risk_amount:,.2f}", f"{entry_price:.2f}", f"{stop_loss_price:.2f}", f"{target_price:.2f}", f"{position_size:,.2f}", f"{total_trade_cost:,.2f}", f"{reward_risk_ratio:.2f}"]
}

df = pd.DataFrame(summary_data)
st.dataframe(df.style.set_properties(**{
    'background-color': '#1e1e1e',
    'color': 'white',
    'border-color': 'gray'
}))

# ─── Chart Visualization ───────────────────────────────────────────────────────
st.subheader("📈 Trade Visualization")

fig, ax = plt.subplots(facecolor="#0e1117")
ax.axhspan(stop_loss_price, entry_price, facecolor='red', alpha=0.3, label="Risk")
ax.axhspan(entry_price, target_price, facecolor='green', alpha=0.3, label="Reward")
ax.axhline(stop_loss_price, color='red', linestyle='--', label=f"Stop Loss ({stop_loss_price})")
ax.axhline(entry_price, color='orange', linestyle='--', label=f"Entry ({entry_price})")
ax.axhline(target_price, color='green', linestyle='--', label=f"Target ({target_price})")

ax.set_xlabel("Trade Setup")
ax.set_ylabel("Price")
ax.set_title("Price Zones", color='white')
ax.legend(loc="center right")
ax.set_facecolor("#0e1117")
ax.tick_params(colors='white')
fig.patch.set_facecolor('#0e1117')

st.pyplot(fig)

# ─── Warnings ───────────────────────────────────────────────────────────────────
if reward_risk_ratio < 2:
    st.warning("⚠️ Warning: Reward-to-risk ratio is below 2:1")

if total_trade_cost > account_balance:
    st.error("🚫 Warning: Trade cost exceeds your available capital!")

# ─── Disclaimers ───────────────────────────────────────────────────────────────
st.markdown("""
---
📢 **Disclaimer**  
This tool is for educational purposes only. It does not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.
""")
