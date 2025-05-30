import streamlit as st
from PIL import Image

# 🧼 Optional: clear old cache if needed
# st.cache_data.clear()  # Uncomment only during development if needed

# ────────────────────────────────────────────────────────────────────────────────
# 📄 Page Setup
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")

# ────────────────────────────────────────────────────────────────────────────────
# 🖼️ Logo
# ────────────────────────────────────────────────────────────────────────────────
logo = Image.open("logo.png")
st.image(logo, width=150)

# ────────────────────────────────────────────────────────────────────────────────
# 📊 App Title
# ────────────────────────────────────────────────────────────────────────────────
st.title("📊 1% Risk Management Calculator")

# ────────────────────────────────────────────────────────────────────────────────
# 🧮 User Inputs
# ────────────────────────────────────────────────────────────────────────────────
account_balance = st.number_input("💰 Account Balance (SEK)", min_value=0.0, value=10000.0)
risk_percent = st.number_input("⚠️ Risk % per trade", min_value=0.0, max_value=100.0, value=1.0)
entry_price = st.number_input("🎯 Entry Price (SEK)", min_value=0.0, value=100.0)
stop_loss_price = st.number_input("🛑 Stop Loss Price (SEK)", min_value=0.0, value=95.0)
target_price = st.number_input("🎯 Target Price (SEK)", min_value=0.0, value=120.0)
leverage = st.number_input("📈 Leverage (e.g. 1x, 2x, 5x)", min_value=1.0, value=1.0)

# ────────────────────────────────────────────────────────────────────────────────
# 🧠 Core Calculations
# ────────────────────────────────────────────────────────────────────────────────
risk_amount = account_balance * (risk_percent / 100)
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit
raw_units = position_size
real_units = position_size * leverage
total_trade_cost = entry_price * real_units
reward_per_unit = abs(target_price - entry_price)
reward = reward_per_unit * real_units
reward_risk_ratio = reward / risk_amount if risk_amount > 0 else 0

# ────────────────────────────────────────────────────────────────────────────────
# 📊 Display Results
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Trade Summary")
st.write(f"✅ **Max Risk Allowed:** SEK {risk_amount:,.2f}")
st.write(f"🔢 **Raw Position Size:** {raw_units:,.0f} units")
st.write(f"📈 **Leveraged Position Size:** {real_units:,.0f} units")
st.write(f"💵 **Total Estimated Trade Cost:** SEK {total_trade_cost:,.2f}")
st.write(f"📊 **Expected Reward:** SEK {reward:,.2f}")
st.write(f"📐 **Reward-to-Risk Ratio:** {reward_risk_ratio:.2f}")

# 🔶 Risk Warning
if reward_risk_ratio < 2:
    st.warning("⚠️ Warning: Reward-to-risk ratio is below 2:1!")

# 🔶 Capital Warning
if total_trade_cost > account_balance:
    st.error("🚨 Warning: This trade exceeds your available capital!")

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

agree = st.checkbox("✅ I acknowledge that I have read and understand the disclaimer above.")
if not agree:
    st.warning("Please confirm that you've read the disclaimer to use this calculator.")
