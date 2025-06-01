import streamlit as st
from PIL import Image

# ✅ Must be first Streamlit call
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")
st.cache_data.clear()

# --- Logo (Optional) ---
logo = Image.open("logo.png")
st.image(logo, width=150)

# --- Title and Intro ---
st.title("📊 1% Risk Management Calculator (Pro Edition)")

st.markdown("""
Welcome! This calculator helps you manage position size and risk by:
- 🧮 Calculating trades based on **liquid capital**
- 📉 Suggesting a stop loss to limit losses to a fixed %
- 🔄 Adjusting for **long or short** direction
- ⚖️ Giving your **Reward-to-Risk (R:R) Ratio**
- 🪜 Factoring in leverage and margin required
""")

# --- Section: User Inputs ---
st.subheader("📥 Inputs")

total_capital = st.number_input("💼 Total Capital ($)", min_value=0.000, value=0.000, step=0.001, format="%.3f")
liquid_capital = st.number_input("💧 Liquid Capital for Trading ($)", min_value=0.000, value=0.000, step=0.001, format="%.3f")
risk_percent = st.number_input("⚠️ Risk % per trade", min_value=0.000, max_value=100.000, value=0.000, step=0.001, format="%.3f")

entry_price = st.number_input("🎯 Entry Price ($)", min_value=0.000, value=0.000, step=0.001, format="%.3f")
direction = st.radio("📈 Are you going long or short?", ["Long", "Short"])
target_price = st.number_input("🎯 Target Price ($)", min_value=0.000, value=0.000, step=0.001, format="%.3f")
leverage = st.number_input("🪜 Leverage (e.g. 1 = no leverage)", min_value=1.000, value=1.000, step=0.100, format="%.3f")

# --- Core Calculations ---
risk_amount = liquid_capital * (risk_percent / 100)

# Calculate suggested stop loss
suggested_risk_per_unit = risk_amount / (risk_amount / entry_price)
if direction == "Long":
    suggested_stop = entry_price - suggested_risk_per_unit
else:
    suggested_stop = entry_price + suggested_risk_per_unit

# Stop loss input (user can override suggested value)
stop_loss_price = st.number_input(
    "🛑 Stop Loss Price ($)",
    min_value=0.000,
    value=round(suggested_stop, 3),
    step=0.001,
    format="%.3f"
)

# Position sizing based on actual stop
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit if risk_per_unit != 0 else 0

# Leverage-adjusted margin used
total_trade_cost = (position_size * entry_price) / leverage if leverage > 0 else 0
reward_per_unit = abs(target_price - entry_price)
expected_reward = reward_per_unit * position_size
reward_to_risk = expected_reward / risk_amount if risk_amount > 0 else 0

# --- Section: Output Summary ---
st.subheader("📈 Trade Summary")
st.write(f"💰 Max Risk Allowed: ${risk_amount:,.3f}")
st.write(f"📦 Suggested Position Size: {position_size:,.0f} units")
st.write(f"🛑 Suggested Stop Loss: ${suggested_stop:,.3f}")
st.write(f"💸 Capital Required (with leverage): ${total_trade_cost:,.3f}")
st.write(f"🎯 Expected Reward: ${expected_reward:,.3f}")
st.write(f"⚖️ Reward-to-Risk Ratio: {reward_to_risk:.2f}")

# --- Warnings ---
if reward_to_risk < 2:
    st.warning("⚠️ Reward-to-risk ratio is below 2:1.")
if total_trade_cost > liquid_capital:
    st.error("🚫 This trade exceeds your liquid trading capital!")

# --- Disclaimer ---
st.markdown("---")
st.subheader("📢 Disclaimer")
st.markdown("""
This tool is for **educational purposes only** and does not constitute financial advice.  
Trading involves risk. Always consult a licensed advisor before making financial decisions.
""")

agree = st.checkbox("✅ I understand and accept the terms above.")
if not agree:
    st.warning("Please confirm you understand the disclaimer to continue.")
