import streamlit as st
from PIL import Image

# ✅ Page configuration
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")

# (Optional) Clear cache
st.cache_data.clear()

# 📸 Load and display logo
logo = Image.open("logo.png")
st.image(logo, width=150)

# 🧠 App title
st.title("📊 1% Risk Management Calculator (Pro Edition)")

# 📄 Tool Description
with st.expander("ℹ️ What this tool does"):
    st.markdown("""
    This tool helps you calculate your position size, stop loss, and risk metrics based on:
    - Total capital (for context)
    - Liquid capital (for active trade sizing)
    - Your entry price, stop loss, target, and leverage
    """)

# --- Section: User Inputs ---
st.subheader("📥 Inputs")

total_capital = st.number_input("💼 Total Capital ($)", min_value=0.0, value=0.0)
liquid_capital = st.number_input("💧 Liquid Capital for Trading ($)", min_value=0.0, value=0.0)
risk_percent = st.number_input("⚠️ Risk % per trade", min_value=0.0, max_value=100.0, value=0.0)
entry_price = st.number_input("🎯 Entry Price ($)", min_value=0.0, value=0.0)
direction = st.radio("📈 Are you going long or short?", ["Long", "Short"])
leverage = st.number_input("🪜 Leverage (e.g. 1 = no leverage)", min_value=1.0, value=1.0)

# 🧮 Risk Amount
risk_amount = liquid_capital * (risk_percent / 100)

# --- Suggested Stop Loss Calculation ---
valid_inputs = entry_price > 0 and risk_percent > 0 and liquid_capital > 0 and leverage > 0

if valid_inputs:
    # 1. Calculate risk capital
    risk_amount = liquid_capital * (risk_percent / 100)

    # 2. Estimate position size
    estimated_position_size = (liquid_capital * leverage) / entry_price

    # 3. Calculate the ideal stop loss distance
    risk_per_unit = risk_amount / estimated_position_size

    # 4. Apply direction
    suggested_stop = entry_price - risk_per_unit if direction == "Long" else entry_price + risk_per_unit

else:
    risk_amount = 0.0
    suggested_stop = entry_price  # No stop suggested without valid input

# Apply guard
safe_suggested_stop = max(round(suggested_stop, 2), 0.01)

# --- Stop Loss & Target Price Inputs ---
stop_loss_price = st.number_input(
    "🛑 Stop Loss Price ($)",
    min_value=0.01,
    value=safe_suggested_stop
)

safe_default_target = max(0.01, 0.0)
target_price = st.number_input(
    "🎯 Target Price ($)",
    min_value=0.01,
    value=safe_default_target
)

# --- Core Calculations ---
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit if risk_per_unit > 0 else 0
total_trade_cost = (position_size * entry_price) / leverage if leverage > 0 else 0
reward_per_unit = abs(target_price - entry_price)
expected_reward = reward_per_unit * position_size
reward_to_risk = expected_reward / risk_amount if risk_amount > 0 else 0

# --- Output Summary ---
st.subheader("📈 Trade Summary")
st.write(f"💰 Max Risk Allowed: ${risk_amount:,.2f}")
st.write(f"📦 Suggested Position Size: {position_size:,.0f} units")
st.write(f"💸 Your Capital at Risk (with leverage): ${total_trade_cost:,.2f}")
st.write(f"🎯 Expected Reward: ${expected_reward:,.2f}")
st.write(f"⚖️ Reward-to-Risk Ratio: {reward_to_risk:.2f}")

# --- Warnings ---
if reward_to_risk < 2 and reward_to_risk > 0:
    st.warning("⚠️ Reward-to-risk ratio is below 2:1!")
if total_trade_cost > liquid_capital:
    st.error("🚫 Trade size exceeds your available capital!")

# --- Disclaimer Section ---
st.markdown("---")
st.subheader("📢 Disclaimer")
st.markdown("""
This tool is provided for **educational purposes only** and does not constitute financial advice.

Trading financial instruments involves risk, and you should never invest more than you can afford to lose.  
Always do your own research or consult a licensed financial advisor before making investment decisions.

By using this tool, you acknowledge that you are solely responsible for your trading activity.
""")

agree = st.checkbox("I acknowledge that I have read and understand the disclaimer above.")
if not agree:
    st.warning("Please confirm that you've read the disclaimer to use this calculator.")
