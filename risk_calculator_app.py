import streamlit as st
from PIL import Image

st.cache_data.clear()

# 🖼️ Page setup
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")

# 📸 Load and display logo
logo = Image.open("logo.png")
st.image(logo, width=150)

# 🧠 App title
st.title("📊 1% Risk Management Calculator")

# 📥 User Inputs
account_balance = st.number_input("Account Balance ($)", min_value=0.0, value=10000.0)
risk_percent = st.number_input("Risk % per trade", min_value=0.0, max_value=100.0, value=1.0)
entry_price = st.number_input("Entry Price ($)", min_value=0.0, value=100.0)
stop_loss_price = st.number_input("Stop Loss Price ($)", min_value=0.0, value=95.0)
target_price = st.number_input("Target Price ($)", min_value=0.0, value=120.0)
leverage = st.number_input("Leverage (e.g. 1 = no leverage)", min_value=1.0, value=1.0)

# 🧮 Core Calculations (Fixed)
risk_amount = account_balance * (risk_percent / 100)
risk_per_unit = abs(entry_price - stop_loss_price)

# Correct: Do NOT multiply position size by leverage
position_size = risk_amount / risk_per_unit

# Apply leverage to cost only
total_trade_cost = (position_size * entry_price) / leverage

# Reward per unit and expected reward based on raw position size
reward_per_unit = abs(target_price - entry_price)
expected_reward = reward_per_unit * position_size
reward_to_risk = expected_reward / risk_amount if risk_amount > 0 else 0

# 📊 Results Display
st.subheader("📈 Trade Summary")
st.write(f"💰 Max Risk Allowed: ${risk_amount:,.2f}")
st.write(f"📦 Suggested Position Size:", f"{position_size:,.0f} units")
st.write(f"💸 Your Capital at Risk (with leverage): ${total_trade_cost:,.2f}")
st.write(f"🎯 Expected Reward: ${expected_reward:,.2f}")
st.write(f"⚖️ Reward-to-Risk Ratio: {reward_to_risk:.2f}")

# 🚨 Warnings
if reward_to_risk < 2:
    st.warning("⚠️ Reward-to-risk ratio is below 2:1!")
if total_trade_cost > account_balance:
    st.error("🚫 Trade size exceeds your available capital!")

# ────────────────────────────────────────────────────────────────────────────────
# 📢 Disclaimer
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📢 Disclaimer")
st.markdown("""
This tool is provided for **educational purposes only** and does not constitute financial advice.

Trading financial instruments involves risk, and you should never invest more than you can afford to lose.  
Always do your own research or consult a licensed financial advisor before making investment decisions.

By using this tool, you acknowledge that you are solely responsible for your trading activity.
""")

# Optional: User acknowledgment checkbox
agree = st.checkbox("I acknowledge that I have read and understand the disclaimer above.")
if not agree:
    st.warning("Please confirm that you've read the disclaimer to use this calculator.")
