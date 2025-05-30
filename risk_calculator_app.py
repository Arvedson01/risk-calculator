import streamlit as st

# ─── Page Setup ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")
st.title("📊 1% Risk Management Calculator (Pro Edition)")

# ─── Tool Description ───────────────────────────────────────────────────────
st.markdown("""
This tool helps you calculate your position size, stop loss, and risk metrics based on:
- Total capital (for context)
- Liquid capital (for actual trade sizing)
- Entry, direction (long/short), target, and leverage
- Automatically calculates your stop loss and RR ratio to stay within risk
""")

# ─── Inputs ─────────────────────────────────────────────────────────────────
total_capital = st.number_input("💼 Total Capital (all holdings)", min_value=0.0, value=120000.0)
liquid_capital = st.number_input("💧 Liquid Capital (available to trade)", min_value=0.0, value=60000.0)
risk_percent = st.number_input("⚠️ Risk % per trade", min_value=0.1, max_value=100.0, value=1.0)
entry_price = st.number_input("🎯 Entry Price", min_value=0.0001, value=1.0)
target_price = st.number_input("🎯 Target Price", min_value=0.0001, value=1.5)
direction = st.radio("📈 Trade Direction", ["Long", "Short"], horizontal=True)
leverage = st.number_input("⚙️ Leverage (e.g. 1 = no leverage)", min_value=1.0, value=1.0)

# ─── Core Logic ─────────────────────────────────────────────────────────────
risk_amount = liquid_capital * (risk_percent / 100)

# Position size: how many units you can buy without exceeding risk
# We'll use a temporary risk_per_unit to reverse-engineer stop loss
position_size = None
stop_loss_price = None
risk_per_unit = None

# Calculate stop loss price based on 1% risk
position_size = 1  # Start from 1 unit temporarily
risk_per_unit = risk_amount / position_size

if direction == "Long":
    stop_loss_price = entry_price - (risk_amount / 1)  # to be corrected later
else:
    stop_loss_price = entry_price + (risk_amount / 1)

# Now calculate correct position size based on proper stop distance
true_risk_per_unit = abs(entry_price - stop_loss_price)
position_size = risk_amount / true_risk_per_unit

# Calculate reward and RR ratio
reward_per_unit = abs(target_price - entry_price)
expected_reward = reward_per_unit * position_size
reward_to_risk = expected_reward / risk_amount if risk_amount else 0

# Calculate leveraged margin used
gross_trade_value = position_size * entry_price
margin_required = gross_trade_value / leverage

# ─── Output ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Trade Summary")
st.write(f"🔹 Max Risk (1%): {risk_amount:,.2f}")
st.write(f"🔹 Suggested Stop Loss: {stop_loss_price:.5f} ({direction})")
st.write(f"🔹 Position Size: {position_size:,.0f} units")
st.write(f"🔹 Gross Trade Value: {gross_trade_value:,.2f}")
st.write(f"🔹 Margin Required (with {leverage:.1f}×): {margin_required:,.2f}")
st.write(f"🔹 Expected Reward: {expected_reward:,.2f}")
st.write(f"🔹 Reward-to-Risk Ratio: {reward_to_risk:.2f}")

# ─── Warnings ───────────────────────────────────────────────────────────────
if reward_to_risk < 2:
    st.warning("⚠️ R:R is below 2:1 — trade may not be worth it.")
if margin_required > liquid_capital:
    st.error("🚫 Margin required exceeds your liquid capital!")
if stop_loss_price <= 0:
    st.error("❌ Invalid stop loss. Entry too small or risk too large.")

# ─── Disclaimer ─────────────────────────────────────────────────────────────
st.markdown("""
---
📢 **Disclaimer**
This tool is for educational purposes only and does not constitute financial advice.
Always do your own research and consult a financial advisor before making trading decisions.
""")
