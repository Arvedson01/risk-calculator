import streamlit as st
from PIL import Image

# ✅ Page configuration MUST be here
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
    - It will even suggest where your stop loss and RR ratio is — if you're unsure!
    """)

# --- Section: User Inputs ---
st.subheader("📥 Inputs")
# ... other inputs like entry_price, capital, etc.

# --- Section: Suggested Stop Logic ---
if entry_price > 0:
    suggested_stop = entry_price * 0.97  # Example: 3% stop below entry
else:
    suggested_stop = 0.0

# Fix to avoid StreamlitValueBelowMinError
safe_suggested_stop = max(round(suggested_stop, 2), 0.01)

# --- Section: Stop Loss Input ---
stop_loss_price = st.number_input(
    "🛑 Stop Loss Price ($) (Suggested: {:.2f})".format(safe_suggested_stop),
    min_value=0.01,
    value=safe_suggested_stop
)

# 🧮 Stop Loss Suggestion
# Calculate stop loss that aligns with 1% risk on liquid capital
risk_amount = liquid_capital * (risk_percent / 100)
stop_loss_buffer = risk_amount / leverage / 1000  # crude estimate
if direction == "Long":
    suggested_stop = entry_price - stop_loss_buffer
else:
    suggested_stop = entry_price + stop_loss_buffer

stop_loss_price = st.number_input("🛑 Stop Loss Price ($) (Suggested: {:.2f})".format(suggested_stop), min_value=0.01, value=round(suggested_stop, 2))
target_price = st.number_input("🎯 Target Price ($)", min_value=0.01, value=22.00)

# 🧮 Core Calculations
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit
total_trade_cost = (position_size * entry_price) / leverage
reward_per_unit = abs(target_price - entry_price)
expected_reward = reward_per_unit * position_size
reward_to_risk = expected_reward / risk_amount if risk_amount > 0 else 0

# 📊 Results
st.subheader("📈 Trade Summary")
st.write(f"💰 Max Risk Allowed: ${risk_amount:,.2f}")
st.write(f"📦 Suggested Position Size: {position_size:,.0f} units")
st.write(f"💸 Your Capital at Risk (with leverage): ${total_trade_cost:,.2f}")
st.write(f"🎯 Expected Reward: ${expected_reward:,.2f}")
st.write(f"⚖️ Reward-to-Risk Ratio: {reward_to_risk:.2f}")

# 🚨 Warnings
if reward_to_risk < 2:
    st.warning("⚠️ Reward-to-risk ratio is below 2:1!")
if total_trade_cost > liquid_capital:
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

agree = st.checkbox("I acknowledge that I have read and understand the disclaimer above.")
if not agree:
    st.warning("Please confirm that you've read the disclaimer to use this calculator.")
