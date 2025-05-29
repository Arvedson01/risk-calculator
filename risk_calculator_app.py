import streamlit as st
from PIL import Image

st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")

# Load and display logo
logo = Image.open("logo.png")
st.image(logo, width=150)
import streamlit as st
st.title("📊 1% Risk Management Calculator")
account_balance = st.number_input("Account Balance (SEK)", min_value=1.0, value=10000.0)
risk_percent = st.number_input("Risk % per trade", min_value=0.1, max_value=100.0, value=1.0)
entry_price = st.number_input("Entry Price (SEK)", min_value=0.01, value=100.0)
stop_loss_price = st.number_input("Stop Loss Price (SEK)", min_value=0.01, value=95.0)
target_price = st.number_input("Target Price (SEK)", min_value=0.01, value=120.0)

risk_amount = account_balance * (risk_percent / 100)
risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / risk_per_unit
reward_per_unit = abs(target_price - entry_price)
reward_to_risk = reward_per_unit / risk_per_unit
total_trade_cost = position_size * entry_price

st.subheader("🧾 Trade Summary")
st.write(f"**Max Risk Allowed:** {risk_amount:.2f} SEK")
st.write(f"**Risk Per Unit:** {risk_per_unit:.2f} SEK")
st.write(f"**Suggested Position Size:** {int(position_size)} units")
st.write(f"**Total Trade Cost:** {total_trade_cost:.2f} SEK")
st.write(f"**Reward-to-Risk Ratio:** {reward_to_risk:.2f}")

if reward_to_risk < 2:
    st.warning("⚠️ Reward-to-risk ratio is below 2:1")
if total_trade_cost > account_balance:
    st.warning("⚠️ Trade size exceeds your available capital")
