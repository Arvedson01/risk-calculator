import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

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
account_balance = st.number_input("💰 Account Balance", min_value=0.0, value=10000.0)
risk_percent = st.number_input("⚠️ Risk % per trade", min_value=0.0, max_value=100.0, value=1.0)
entry_price = st.number_input("🎯 Entry Price", min_value=0.0, value=100.0)
stop_loss_price = st.number_input("🛑 Stop Loss Price", min_value=0.0, value=95.0)
target_price = st.number_input("🎯 Target Price", min_value=0.0, value=120.0)
leverage = st.number_input("📈 Leverage (e.g. 1x, 2x, 5x)", min_value=1.0, value=1.0)

# ────────────────────────────────────────────────────────────────────────────────
# ✅ Validity Check Before Calculations
# ────────────────────────────────────────────────────────────────────────────────
if stop_loss_price == entry_price:
    st.error("❌ Entry and Stop Loss price cannot be the same.")
elif target_price == entry_price:
    st.error("❌ Entry and Target price cannot be the same.")
elif account_balance <= 0 or risk_percent <= 0:
    st.info("ℹ️ Enter a valid account balance and risk %.")
else:
    # ────────────────────────────────────────────────────────────────────────────
    # 📐 Calculations
    # ────────────────────────────────────────────────────────────────────────────
    risk_amount = account_balance * (risk_percent / 100)
    risk_per_unit = abs(entry_price - stop_loss_price)
    position_size = risk_amount / risk_per_unit
    leveraged_size = position_size * leverage
    total_trade_cost = entry_price * leveraged_size
    reward_per_unit = abs(target_price - entry_price)
    reward = reward_per_unit * leveraged_size
    reward_risk_ratio = reward / risk_amount if risk_amount > 0 else 0

    # ────────────────────────────────────────────────────────────────────────────
    # 📊 Results Summary (Metric Columns)
    # ────────────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📈 Trade Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Amount", f"{risk_amount:,.2f}")
    col2.metric("Position Size", f"{position_size:,.0f} units")
    col3.metric("With Leverage", f"{leveraged_size:,.0f} units")

    col4, col5, col6 = st.columns(3)
    col4.metric("Trade Cost", f"{total_trade_cost:,.2f}")
    col5.metric("Expected Reward", f"{reward:,.2f}")
    col6.metric("R:R Ratio", f"{reward_risk_ratio:.2f}")

    # Warnings
    if reward_risk_ratio < 2:
        st.warning("⚠️ Reward-to-risk ratio is below 2:1!")
    if total_trade_cost > account_balance:
        st.error("🚨 Trade size exceeds your available capital!")

    # ────────────────────────────────────────────────────────────────────────────
    # 📉 Chart
    # ────────────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📉 Trade Visualization")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axhspan(min(stop_loss_price, entry_price), max(stop_loss_price, entry_price),
               facecolor='red', alpha=0.3, label="Risk")
    ax.axhspan(min(entry_price, target_price), max(entry_price, target_price),
               facecolor='green', alpha=0.3, label="Reward")
    ax.axhline(stop_loss_price, color='red', linestyle='--', label=f'Stop Loss ({stop_loss_price})')
    ax.axhline(entry_price, color='orange', linestyle='--', label=f'Entry ({entry_price})')
    ax.axhline(target_price, color='green', linestyle='--', label=f'Target ({target_price})')

    ax.set_title("Price Zones")
    ax.set_xlabel("Trade Setup")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

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
