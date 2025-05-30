import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# 🔧 Setup
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="📊 Risk Calculator", page_icon="📈")

# Logo
logo = Image.open("logo.png")
st.image(logo, width=150)

st.title("📊 1% Risk Management Calculator")

# ─────────────────────────────────────────────────────────────────────────────
# 📥 Inputs
# ─────────────────────────────────────────────────────────────────────────────
account_balance = st.number_input("Account Balance", min_value=0.0, value=10000.0)
risk_percent = st.number_input("Risk % per trade", min_value=0.0, value=1.0)
entry_price = st.number_input("Entry Price", min_value=0.0, value=100.0)
stop_loss_price = st.number_input("Stop Loss", min_value=0.0, value=95.0)
target_price = st.number_input("Target Price", min_value=0.0, value=120.0)
leverage = st.number_input("Leverage (e.g. 1x, 2x, 5x)", min_value=1.0, value=1.0)

# ─────────────────────────────────────────────────────────────────────────────
# 🧮 Calculations
# ─────────────────────────────────────────────────────────────────────────────
risk_amount = account_balance * (risk_percent / 100)
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit
leveraged_position_size = position_size * leverage
total_trade_cost = leveraged_position_size * entry_price
reward_per_unit = abs(target_price - entry_price)
expected_reward = reward_per_unit * leveraged_position_size
reward_risk_ratio = expected_reward / risk_amount if risk_amount > 0 else 0

# ─────────────────────────────────────────────────────────────────────────────
# 📊 Metrics
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Trade Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Risk Amount", f"{risk_amount:,.2f}")
col2.metric("Position Size", f"{leveraged_position_size:,.0f} units")
col3.metric("Trade Cost", f"{total_trade_cost:,.2f}")

col4, col5, col6 = st.columns(3)
col4.metric("Expected Reward", f"{expected_reward:,.2f}")
col5.metric("Reward/Unit", f"{reward_per_unit:,.2f}")
col6.metric("R:R Ratio", f"{reward_risk_ratio:.2f}")

# Warnings
if reward_risk_ratio < 2:
    st.warning("⚠️ Reward-to-risk ratio is below 2:1")
if total_trade_cost > account_balance:
    st.error("🚫 Trade cost exceeds your account balance")

# ─────────────────────────────────────────────────────────────────────────────
# 📉 Chart
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("📉 Trade Visualization")

fig, ax = plt.subplots(figsize=(6, 4))
ax.axhspan(min(stop_loss_price, entry_price), max(stop_loss_price, entry_price), facecolor='red', alpha=0.3, label="Risk")
ax.axhspan(min(entry_price, target_price), max(entry_price, target_price), facecolor='green', alpha=0.3, label="Reward")
ax.axhline(stop_loss_price, color='red', linestyle='--', label=f"Stop Loss ({stop_loss_price})")
ax.axhline(entry_price, color='orange', linestyle='--', label=f"Entry ({entry_price})")
ax.axhline(target_price, color='green', linestyle='--', label=f"Target ({target_price})")

# Dark theme styling
fig.patch.set_facecolor('#0e1117')
ax.set_facecolor('#0e1117')
ax.tick_params(colors='white')
ax.yaxis.label.set_color('white')
ax.xaxis.label.set_color('white')
ax.title.set_color('white')
ax.grid(True, color='#444444')
ax.set_title("Price Zones")
ax.set_xlabel("Trade Setup")
ax.set_ylabel("Price")
ax.legend()
st.pyplot(fig)

# ─────────────────────────────────────────────────────────────────────────────
# 📘 Disclaimer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("📌 **Disclaimer:** This tool is for educational purposes only and does not constitute financial advice.")
st.markdown("💡 Always consult with a certified financial advisor before making trading decisions.")
