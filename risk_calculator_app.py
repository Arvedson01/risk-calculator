import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")

# Logo
logo = Image.open("logo.png")
st.image(logo, width=150)

# Title
st.title("📊 1% Risk Management Calculator")

# Inputs
account_balance = st.number_input("💰 Account Balance (SEK)", min_value=0.0, value=10000.0)
risk_percent = st.number_input("⚠️ Risk % per trade", min_value=0.0, max_value=100.0, value=1.0)
entry_price = st.number_input("🎯 Entry Price (SEK)", min_value=0.0, value=100.0)
stop_loss_price = st.number_input("🛑 Stop Loss Price (SEK)", min_value=0.0, value=95.0)
target_price = st.number_input("🎯 Target Price (SEK)", min_value=0.0, value=120.0)
leverage = st.number_input("📈 Leverage (e.g. 1x, 2x, 5x)", min_value=1.0, value=1.0)

# Calculations
risk_amount = account_balance * (risk_percent / 100)
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit
adjusted_position_size = position_size * leverage
total_trade_cost = entry_price * adjusted_position_size
reward_per_unit = abs(target_price - entry_price)
reward = reward_per_unit * adjusted_position_size
reward_risk_ratio = reward / risk_amount if risk_amount > 0 else 0

# Output
st.subheader("📈 Trade Summary")
st.write(f"✅ **Max Risk Allowed:** SEK {risk_amount:,.2f}")
st.write(f"🔢 **Raw Position Size:** {position_size:,.0f} units")
st.write(f"📈 **Leveraged Position Size:** {adjusted_position_size:,.0f} units")
st.write(f"💵 **Total Estimated Trade Cost:** SEK {total_trade_cost:,.2f}")
st.write(f"📊 **Expected Reward:** SEK {reward:,.2f}")
st.write(f"📐 **Reward-to-Risk Ratio:** {reward_risk_ratio:.2f}")

# Warnings
if reward_risk_ratio < 2:
    st.warning("⚠️ Warning: Reward-to-risk ratio is below 2:1!")
if total_trade_cost > account_balance:
    st.error("🚨 Warning: This trade exceeds your available capital!")

# Chart
st.subheader("📉 Trade Visualization")

fig, ax = plt.subplots(figsize=(6, 4))

# Highlight areas
ax.axhspan(stop_loss_price, entry_price, facecolor='red', alpha=0.3, label="Risk")
ax.axhspan(entry_price, target_price, facecolor='green', alpha=0.3, label="Reward")

# Horizontal lines
ax.axhline(stop_loss_price, color='red', linestyle='--', label=f'Stop Loss ({stop_loss_price})')
ax.axhline(entry_price, color='orange', linestyle='--', label=f'Entry ({entry_price})')
ax.axhline(target_price, color='green', linestyle='--', label=f'Target ({target_price})')

# Chart formatting
ax.set_title("Price Zones")
ax.set_xlabel("Trade Setup")
ax.set_ylabel("Price (SEK)")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# Disclaimer
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
