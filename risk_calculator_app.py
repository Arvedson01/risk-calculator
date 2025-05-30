import streamlit as st
from PIL import Image

# Page configuration MUST be here
st.set_page_config(page_title="1% Risk Calculator", page_icon="")

# (Optional) Clear cache
st.cache_data.clear()

# Load and display logo
logo = Image.open("logo.png")
st.image(logo, width=150)

# App title
st.title(" 1% Risk Management Calculator (Pro Edition)")

# Tool Description
with st.expander(" What this tool does"):
    st.markdown("""
    This tool helps you calculate your position size, stop loss, and risk metrics based on:
    - Total capital (for context)
    - Liquid capital (for active trade sizing)
    - Your entry price, stop loss, target, and leverage
    - It will even suggest where your stop loss and RR ratio is — if you're unsure!
    - *Now includes commission costs* for more accurate risk calculations
    """)

# User Inputs
st.subheader(" Inputs")
total_capital = st.number_input(" Total Capital ($)", min_value=0.0, value=0.0)
liquid_capital = st.number_input(" Liquid Capital for Trading ($)", min_value=0.0, value=0.0)
risk_percent = st.number_input(" Risk % per trade", min_value=0.1, max_value=100.0, value=1.0)
entry_price = st.number_input(" Entry Price ($)", min_value=0.0, value=0.0)
direction = st.radio(" Are you going long or short?", ["Long", "Short"])
leverage = st.number_input(" Leverage (e.g. 1 = no leverage)", min_value=1.0, value=1.0)

# Stop Loss Suggestion
# Calculate stop loss that aligns with 1% risk on liquid capital
risk_amount = liquid_capital * (risk_percent / 100)
stop_loss_buffer = risk_amount / leverage / 1000  # crude estimate
if direction == "Long":
    suggested_stop = entry_price - stop_loss_buffer
else:
    suggested_stop = entry_price + stop_loss_buffer

stop_loss_price = st.number_input(" Stop Loss Price ($) (Suggested: {:.2f})".format(suggested_stop), 
                                  min_value=0.0, value=0.0)
target_price = st.number_input(" Target Price ($)", min_value=0.0, value=0.0)

# Broker Commission Input
st.subheader(" Broker Commission")
commission_per_side = st.number_input(" Commission per side ($)", min_value=0.0, value=0.0, 
                                     help="Commission paid when entering AND exiting the trade")

# Core Calculations
# Calculate total commission (entry + exit)
total_commission = 2 * commission_per_side

# Calculate risk per unit and position size
risk_per_unit = abs(entry_price - stop_loss_price)
if risk_per_unit > 0:
    position_size = (risk_amount - total_commission) / risk_per_unit
    position_size = max(position_size, 0)  # Ensure non-negative
else:
    position_size = 0

# Calculate trade costs and profits
total_trade_cost_without_commission = (position_size * entry_price) / leverage
total_trade_cost = total_trade_cost_without_commission + commission_per_side  # Only entry commission paid upfront

price_difference = abs(target_price - entry_price)
expected_reward_without_commission = price_difference * position_size
expected_reward = expected_reward_without_commission - total_commission  # Deduct both entry and exit commissions

# Calculate reward-to-risk ratio
if risk_amount > 0:
    reward_to_risk = expected_reward / risk_amount
else:
    reward_to_risk = 0

# Results
st.subheader(" Trade Summary")
st.write(f" Max Risk Allowed: ${risk_amount:,.2f}")
st.write(f" Total Commission (entry + exit): ${total_commission:,.2f}")
st.write(f" Position Size: {position_size:,.2f} units")
st.write(f" Capital Required (without commission): ${total_trade_cost_without_commission:,.2f}")
st.write(f" Capital Required (with entry commission): ${total_trade_cost:,.2f}")
st.write(f" Expected Profit (without commission): ${expected_reward_without_commission:,.2f}")
st.write(f" Expected Profit (after commissions): ${expected_reward:,.2f}")
st.write(f" Reward-to-Risk Ratio (after commission): {reward_to_risk:.2f}")

# Warnings
if reward_to_risk < 2 and reward_to_risk > 0:
    st.warning(" Reward-to-risk ratio is below 2:1 (after considering commission)!")
elif reward_to_risk <= 0 and risk_amount > 0:
    st.warning(" Reward-to-risk ratio is not positive.")
    
if total_trade_cost > liquid_capital and liquid_capital > 0:
    st.error(" Trade cost (including commission) exceeds your available capital!")
elif liquid_capital <= 0 and total_trade_cost > 0:
    st.error(" Liquid capital is zero or negative, cannot calculate trade cost.")

if total_commission > risk_amount and risk_amount > 0:
    st.error(" Commission costs exceed your maximum risk amount!")

# ────────────────────────────────────────────────────────────────────────────────
# Disclaimer
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader(" Disclaimer")
st.markdown("""
This tool is provided for educational purposes only and does not constitute financial advice.

Trading financial instruments involves risk, and you should never invest more than you can afford to lose.
Always do your own research or consult a licensed financial advisor before making investment decisions.

By using this tool, you acknowledge that you are solely responsible for your trading activity.
""")

agree = st.checkbox("I acknowledge that I have read and understand the disclaimer above.")
if not agree:
    st.warning("Please confirm that you've read the disclaimer to use this calculator.")
