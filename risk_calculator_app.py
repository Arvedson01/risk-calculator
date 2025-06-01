import streamlit as st
from PIL import Image

# ────────────────────────────────────────────────────────────────────────────────
# 📄 Page Setup (must be first Streamlit call)
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="1% Risk Calculator", page_icon="📊")
st.cache_data.clear()

# ────────────────────────────────────────────────────────────────────────────────
# 🖼️ Logo (optional)
# ────────────────────────────────────────────────────────────────────────────────
logo = Image.open("logo.png")
st.image(logo, width=150)

# ────────────────────────────────────────────────────────────────────────────────
# 📊 Title & Intro
# ────────────────────────────────────────────────────────────────────────────────
st.title("📊 1% Risk Management Calculator (Pro Edition)")

st.markdown("""
This calculator helps you:
- 🧮 Risk exactly 1% of your **liquid capital** per trade
- 🛑 Suggest a stop loss that is 1% away from your entry (long or short)
- 🎯 Show reward-to-risk based on your chosen target price
- 🪜 Factor in leverage to calculate **capital required**
- ⚠️ Warn if your capital or risk rules would be violated
""")

# ────────────────────────────────────────────────────────────────────────────────
# 📝 Section: User Inputs (all with 3-decimal precision)
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("📥 Inputs")

total_capital = st.number_input(
    "💼 Total Capital ($)",
    min_value=0.000,
    value=0.000,
    step=0.001,
    format="%.3f"
)

liquid_capital = st.number_input(
    "💧 Liquid Capital for Trading ($)",
    min_value=0.000,
    value=0.000,
    step=0.001,
    format="%.3f"
)

risk_percent = st.number_input(
    "⚠️ Risk % per trade",
    min_value=0.000,
    max_value=100.000,
    value=1.000,
    step=0.001,
    format="%.3f"
)

entry_price = st.number_input(
    "🎯 Entry Price ($)",
    min_value=0.000,
    value=0.000,
    step=0.001,
    format="%.3f"
)

direction = st.radio("📈 Are you going long or short?", ["Long", "Short"])

target_price = st.number_input(
    "🎯 Target Price ($)",
    min_value=0.000,
    value=0.000,
    step=0.001,
    format="%.3f"
)

leverage = st.number_input(
    "🪜 Leverage (e.g. 1 = no leverage)",
    min_value=1.000,
    value=1.000,
    step=0.100,
    format="%.3f"
)

# ────────────────────────────────────────────────────────────────────────────────
# 🧮 Core Calculations
# ────────────────────────────────────────────────────────────────────────────────
# 1) How much you can risk in $ (1% of your liquid capital)
risk_amount = liquid_capital * (risk_percent / 100)

# 2) Suggest a stop-loss exactly 1% away from entry
#    (long → stop = entry – 1%; short → stop = entry + 1%)
delta = entry_price * (risk_percent / 100)

if direction == "Long":
    suggested_stop = entry_price - delta
else:  # Short
    suggested_stop = entry_price + delta

# 3) Let user override suggested stop (with 3-decimals)
stop_loss_price = st.number_input(
    "🛑 Stop Loss Price ($)",
    min_value=0.000,
    value=round(suggested_stop, 3),
    step=0.001,
    format="%.3f"
)

# 4) Now recalc risk per unit based on actual stop
risk_per_unit = abs(entry_price - stop_loss_price) if stop_loss_price != entry_price else 0.000

# 5) Position size so that (risk_per_unit × units) = risk_amount
position_size = (risk_amount / risk_per_unit) if risk_per_unit > 0 else 0.000

# 6) Capital required (margin) = (position_size × entry_price) ÷ leverage
capital_required = (position_size * entry_price) / leverage if leverage > 0 else 0.000

# 7) Reward-to-risk calculation
reward_per_unit = abs(target_price - entry_price)
expected_reward = reward_per_unit * position_size
reward_to_risk = (expected_reward / risk_amount) if risk_amount > 0 else 0.000

# ────────────────────────────────────────────────────────────────────────────────
# 📈 Output: Trade Summary
# ────────────────────────────────────────────────────────────────────────────────
st.subheader("📈 Trade Summary")

st.write(f"💰 Max Risk Allowed: ${risk_amount:,.3f}")
st.write(f"📦 Suggested Position Size: {position_size:,.0f} units")
st.write(f"🛑 Suggested Stop Loss: ${suggested_stop:,.3f}")
st.write(f"💸 Capital Required (with leverage): ${capital_required:,.3f}")
st.write(f"🎯 Expected Reward: ${expected_reward:,.3f}")
st.write(f"⚖️ Reward-to-Risk Ratio: {reward_to_risk:.2f}")

# ────────────────────────────────────────────────────────────────────────────────
# 🚨 Warnings
# ────────────────────────────────────────────────────────────────────────────────
if reward_to_risk < 2:
    st.warning("⚠️ Reward-to-risk ratio is below 2:1.")

if capital_required > liquid_capital:
    st.error("🚫 This trade exceeds your liquid trading capital!")

# ────────────────────────────────────────────────────────────────────────────────
# 📢 Disclaimer
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📢 Disclaimer")
st.markdown("""
This tool is provided for **educational purposes only** and does not constitute financial advice.

Trading involves risk. Always consult a licensed financial advisor and only use capital you can afford to lose.
""")

agree = st.checkbox("✅ I understand and accept the disclaimer.")
if not agree:
    st.warning("Please acknowledge the disclaimer to proceed.")
