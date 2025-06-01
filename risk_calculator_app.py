import streamlit as st
from PIL import Image
from typing import Literal, Tuple

# Constants
DEFAULT_RISK_PERCENT = 1.000
MIN_LEVERAGE = 1.000
MIN_REWARD_RISK_RATIO = 2.000

# ────────────────────────────────────────────────────────────────────────────────
# 📄 Page Setup (must be first Streamlit call)
# ────────────────────────────────────────────────────────────────────────────────
def setup_page():
    """Configure page settings and clear cache."""
    st.set_page_config(
        page_title="1% Risk Calculator",
        page_icon="📊",
        layout="centered"
    )
    st.cache_data.clear()

# ────────────────────────────────────────────────────────────────────────────────
# 🖼️ Logo and Header
# ────────────────────────────────────────────────────────────────────────────────
def display_header(logo_path: str = "logo.png"):
    """Display logo and introductory content."""
    try:
        logo = Image.open(logo_path)
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(logo, width=150)
        with col2:
            st.title("📊 1% Risk Management Calculator (Pro Edition)")
    except FileNotFoundError:
        st.title("📊 1% Risk Management Calculator (Pro Edition)")
    
    st.markdown("""
    This calculator helps you:
    - 🧮 Risk exactly 1% of your **liquid capital** per trade
    - 🛑 Calculate optimal position size and stop loss
    - 🎯 Show reward-to-risk based on your chosen target price
    - 🪜 Factor in leverage to calculate **capital required**
    - ⚠️ Warn if your capital or risk rules would be violated
    """)

# ────────────────────────────────────────────────────────────────────────────────
# 📝 User Inputs (re‐arranged into two equal columns)
# ────────────────────────────────────────────────────────────────────────────────
def get_user_inputs() -> Tuple[float, float, float, float, Literal["Long", "Short"], float, float]:
    """Collect and return all user inputs in a two‐column layout."""
    col1, col2 = st.columns(2)

    with col1:
        total_capital = st.number_input(
            "💼 Total Capital ($)",
            min_value=0.000,
            value=10000.000,
            step=0.001,
            format="%.3f"
        )

        liquid_capital = st.number_input(
            "💧 Liquid Capital for Trading ($)",
            min_value=0.000,
            value=10000.000,
            step=0.001,
            format="%.3f"
        )

        risk_percent = st.number_input(
            "⚠️ Risk % per trade",
            min_value=0.001,
            max_value=100.000,
            value=DEFAULT_RISK_PERCENT,
            step=0.001,
            format="%.3f"
        )

        entry_price = st.number_input(
            "🎯 Entry Price ($)",
            min_value=0.001,
            value=100.000,
            step=0.001,
            format="%.3f"
        )

    with col2:
        direction = st.radio(
            "📈 Are you going long or short?",
            ["Long", "Short"],
            horizontal=True
        )

        # We put a “dummy” Stop Loss here just to balance the columns.
        # It will be overridden by the actual suggestion later.
        dummy_stop = st.number_input(
            "🛑 Stop Loss Price ($)",
            min_value=0.000,
            value=99.000,
            step=0.001,
            format="%.3f"
        )

        target_price = st.number_input(
            "🎯 Target Price ($)",
            min_value=0.000,
            value=105.000,
            step=0.001,
            format="%.3f"
        )

        leverage = st.number_input(
            "🪜 Leverage (e.g. 1 = no leverage)",
            min_value=MIN_LEVERAGE,
            value=1.000,
            step=0.001,
            format="%.3f"
        )

    return total_capital, liquid_capital, risk_percent, entry_price, direction, target_price, leverage

# ────────────────────────────────────────────────────────────────────────────────
# 🧮 Core Calculations
# ────────────────────────────────────────────────────────────────────────────────
def calculate_trade_metrics(
    liquid_capital: float,
    risk_percent: float,
    entry_price: float,
    direction: Literal["Long", "Short"],
    target_price: float,
    leverage: float
) -> Tuple[float, float, float, float, float, float, float]:
    """Calculate all trade metrics based on user inputs."""
    # 1) Calculate maximum allowed risk in dollars
    risk_amount = liquid_capital * (risk_percent / 100)

    # 2) Calculate maximum position size (in units) if we used all capital with leverage
    max_position_value = liquid_capital * leverage
    max_units = max_position_value / entry_price if entry_price > 0 else 0.0
    int_max_units = int(max_units)  # round down to whole units
    
    # 3) How much “price distance” per unit would put those max_units at exactly risk_amount?
    if int_max_units > 0:
        required_risk_per_unit = risk_amount / int_max_units
    else:
        required_risk_per_unit = 0.000
    
    # 4) Suggest a stop price based on direction
    if direction == "Long":
        suggested_stop = entry_price - required_risk_per_unit
    else:  # Short
        suggested_stop = entry_price + required_risk_per_unit

    # 5) Now ask the user to confirm/override that suggested stop.
    #    We give it a unique key so it doesn’t collide with the “dummy” from get_user_inputs().
    stop_loss_price = st.number_input(
        "🛑 Stop Loss Price ($)",
        min_value=0.000,
        value=round(suggested_stop, 3),
        step=0.001,
        format="%.3f",
        key="stop_loss_override"   # <— this key is unique
    )

    # 6) Re‐compute actual risk per unit based on what the user entered above
    actual_risk_per_unit = abs(entry_price - stop_loss_price) if stop_loss_price != entry_price else 0.000

    # 7) Final position size so that (actual_risk_per_unit × units) = risk_amount
    if actual_risk_per_unit > 0:
        raw_units = risk_amount / actual_risk_per_unit
        position_size = float(int(raw_units))  # round down to whole units
    else:
        position_size = 0.000

    # 8) Capital required (margin) = (position_size × entry_price) / leverage
    position_value = position_size * entry_price
    capital_required = position_value / leverage if leverage > 0 else 0.000

    # 9) Reward‐to‐risk
    reward_per_unit = abs(target_price - entry_price)
    expected_reward = reward_per_unit * position_size
    reward_to_risk = (expected_reward / risk_amount) if risk_amount > 0 else 0.000

    return (
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        stop_loss_price
    )

# ────────────────────────────────────────────────────────────────────────────────
# 📊 Display Results
# ────────────────────────────────────────────────────────────────────────────────
def display_results(
    risk_amount: float,
    position_size: float,
    suggested_stop: float,
    capital_required: float,
    expected_reward: float,
    reward_to_risk: float,
    liquid_capital: float
):
    """Display the trade summary and warnings."""
    st.subheader("📈 Trade Summary")
    
    # Formatting helpers (strip trailing zeros when not needed)
    def strip_zeros_fmt(fmt_str: str) -> str:
        # e.g. turns "1,234.500" → "1,234.5", and "1,000.000" → "1,000"
        return fmt_str.rstrip('0').rstrip('.') if '.' in fmt_str else fmt_str

    def format_currency(value: float) -> str:
        tmp = f"{value:,.3f}"
        return "$" + strip_zeros_fmt(tmp)
    
    def format_units(value: float) -> str:
        if value == 0:
            return "0 units"
        tmp = f"{value:,.3f}"
        stripped = strip_zeros_fmt(tmp)
        return f"{stripped} units"

    metrics = {
        "💰 Max Risk Allowed": format_currency(risk_amount),
        "📦 Position Size": format_units(position_size),
        "🛑 Suggested Stop Loss": format_currency(suggested_stop),
        "💸 Capital Required": format_currency(capital_required),
        "🎯 Expected Reward": format_currency(expected_reward),
        "⚖️ Reward-to-Risk Ratio": f"{strip_zeros_fmt(f'{reward_to_risk:.3f}')}:1"
    }
    
    for label, value in metrics.items():
        st.metric(label=label, value=value)
    
    # Warnings
    if reward_to_risk < MIN_REWARD_RISK_RATIO:
        st.warning(f"⚠️ Reward-to-Risk ratio is below {MIN_REWARD_RISK_RATIO:.1f}:1. Consider adjusting your target.")

    if capital_required > liquid_capital:
        st.error("🚫 This trade exceeds your liquid trading capital!")
    elif capital_required > 0.8 * liquid_capital:
        st.warning("⚠️ This trade uses more than 80% of your liquid capital. Consider reducing position size.")

# ────────────────────────────────────────────────────────────────────────────────
# 📢 Disclaimer
# ────────────────────────────────────────────────────────────────────────────────
def display_disclaimer():
    """Show disclaimer and get user acknowledgment."""
    st.markdown("---")
    st.subheader("📢 Disclaimer")
    st.markdown("""
    **This tool is provided for educational purposes only** and does not constitute financial advice.
    
    Trading involves risk. Always consult a licensed financial advisor and only use capital you can afford to lose.
    """)
    
    if not st.checkbox("✅ I understand and accept the disclaimer."):
        st.warning("Please acknowledge the disclaimer to proceed.")
        st.stop()

# ────────────────────────────────────────────────────────────────────────────────
# 🚀 Main Application
# ────────────────────────────────────────────────────────────────────────────────
def main():
    setup_page()
    display_header()
    
    # Get user inputs (4 widgets on left, 4 widgets on right)
    total_capital, liquid_capital, risk_percent, entry_price, direction, target_price, leverage = get_user_inputs()
    
    # Perform calculations
    (
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        stop_loss_price
    ) = calculate_trade_metrics(
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage
    )
    
    # Display results and warnings
    display_results(
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        liquid_capital
    )
    
    # Show disclaimer
    display_disclaimer()

if __name__ == "__main__":
    main()
