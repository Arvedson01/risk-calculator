import streamlit as st
from PIL import Image
from typing import Literal, Tuple

# ────────────────────────────────────────────────────────────────────────────────
# 📄 Page Setup (must be the very first Streamlit call)
# ────────────────────────────────────────────────────────────────────────────────
def setup_page():
    st.set_page_config(
        page_title="1% Risk Calculator",
        page_icon="📊",
        layout="centered",
    )
    st.cache_data.clear()


# ────────────────────────────────────────────────────────────────────────────────
# 🖼️ Logo and Header
# ────────────────────────────────────────────────────────────────────────────────
def display_header(logo_path: str = "logo.png"):
    """Display logo (if present) and the title + short bullet list."""
    try:
        logo = Image.open(logo_path)
        col1, col2 = st.columns([1, 4], gap="small")
        with col1:
            st.image(logo, width=150)
        with col2:
            st.title("📊 1% Risk Management Calculator (Pro Edition)")
    except FileNotFoundError:
        st.title("📊 1% Risk Management Calculator (Pro Edition)")

    st.markdown(
        """
        This calculator helps you:
        - 🧮 Risk exactly 1% of your **liquid capital** per trade  
        - 🛑 Calculate an optimal stop‐loss so that you only risk 1%  
        - 🎯 Show reward‐to‐risk based on your chosen target price  
        - 🧬 Factor in leverage to compute **capital required**  
        - ⚠️ Warn if your capital or risk rules would be violated  
        """
    )


# ────────────────────────────────────────────────────────────────────────────────
# 📝 User Inputs (2×4 Grid)
# ────────────────────────────────────────────────────────────────────────────────
def get_user_inputs() -> Tuple[
    float, float, float, float, Literal["Long", "Short"], float, float, float
]:
    """
    Collect all user inputs in a 2×4 layout. 
    Fields accept three decimals under the hood, but display without trailing .000 if unneeded.
    """
    col1, col2 = st.columns(2, gap="small")

    with col1:
        total_capital = st.number_input(
            "💼 Total Capital ($)",
            min_value=0.000,
            value=10000.000,
            step=0.001,
            format="%g",
            key="total_cap",
        )
        liquid_capital = st.number_input(
            "💧 Liquid Capital for Trading ($)",
            min_value=0.000,
            value=10000.000,
            step=0.001,
            format="%g",
            key="liquid_cap",
        )
        risk_percent = st.number_input(
            "⚠️ Risk % per trade",
            min_value=0.001,
            max_value=100.000,
            value=1.000,
            step=0.001,
            format="%g",
            key="risk_pct",
        )
        leverage = st.number_input(
            "🪜 Leverage (e.g. 1 = no leverage)",
            min_value=1.000,
            value=1.000,
            step=0.001,
            format="%g",
            key="leverage",
        )

    with col2:
        entry_price = st.number_input(
            "🎯 Entry Price ($)",
            min_value=0.001,
            value=100.000,
            step=0.001,
            format="%g",
            key="entry_price",
        )
        direction = st.radio(
            "📈 Are you going Long or Short?",
            ["Long", "Short"],
            horizontal=True,
            key="direction",
        )
        target_price = st.number_input(
            "🎯 Target Price ($)",
            min_value=0.000,
            value=105.000,
            step=0.001,
            format="%g",
            key="target_price",
        )
        # placeholder for Stop‐Loss; we’ll supply a default “suggested_stop” below in main()
        # but assign a unique key so it does not clash with other number_inputs.
        stop_loss_price = st.number_input(
            "🛑 Stop Loss Price ($)",
            min_value=0.000,
            value=0.000,
            step=0.001,
            format="%g",
            key="stop_loss_price",
            help="This is pre‐filled with a suggestion, but you can override it.",
        )

    return (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
        stop_loss_price,
    )


# ────────────────────────────────────────────────────────────────────────────────
# 🧮 Core Calculations
# ────────────────────────────────────────────────────────────────────────────────
def calculate_trade_metrics(
    liquid_capital: float,
    risk_percent: float,
    entry_price: float,
    direction: Literal["Long", "Short"],
    target_price: float,
    leverage: float,
    stop_loss_price: float,
) -> Tuple[
    float,  # risk_amount
    float,  # position_size
    float,  # suggested_stop
    float,  # capital_required
    float,  # expected_reward
    float,  # reward_to_risk
]:
    """
    1) risk_amount = liquid_capital * (risk_percent/100)
    2) max_units = (liquid_capital * leverage) / entry_price
    3) required_risk_per_unit = risk_amount / max_units
    4) suggested_stop = entry_price ± required_risk_per_unit (Long vs. Short)
    5) actual_risk_per_unit = |entry_price - stop_loss_price|
    6) position_size = risk_amount / actual_risk_per_unit
    7) capital_required = (position_size * entry_price) / leverage
    8) reward computations
    """
    # 1) Dollar amount you are risking
    risk_amount = liquid_capital * (risk_percent / 100)

    # 2) Theoretical max units if you used all margin
    max_position_value = liquid_capital * leverage
    max_units = (max_position_value / entry_price) if entry_price > 0 else 0.0

    # 3) Required risk per unit for exactly 1%
    required_risk_per_unit = (risk_amount / max_units) if max_units > 0 else 0.0

    # 4) Suggested stop (before override)
    if direction == "Long":
        suggested_stop = entry_price - required_risk_per_unit
    else:  # Short
        suggested_stop = entry_price + required_risk_per_unit

    # 5) Actual risk per unit (based on user‐entered stop_loss_price)
    actual_risk_per_unit = abs(entry_price - stop_loss_price) if stop_loss_price != entry_price else 0.0

    # 6) Position size that exactly risks risk_amount
    position_size = (risk_amount / actual_risk_per_unit) if actual_risk_per_unit > 0 else 0.0

    # 7) Capital required (accounting for leverage)
    position_value = position_size * entry_price
    capital_required = (position_value / leverage) if leverage > 0 else 0.0

    # 8) Reward computations
    reward_per_unit = abs(target_price - entry_price)
    expected_reward = reward_per_unit * position_size
    reward_to_risk = (expected_reward / risk_amount) if risk_amount > 0 else 0.0

    return (
        risk_amount,
        position_size,
        round(suggested_stop, 3),
        capital_required,
        expected_reward,
        reward_to_risk,
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
    liquid_capital: float,
):
    """Show the trade summary metrics and any warnings."""
    st.subheader("📈 Trade Summary")

    def format_currency(val: float) -> str:
        if abs(val) < 0.001:
            return "$0.000"
        # Show 3 decimals if there is any fractional part; otherwise, show whole number
        return f"${val:,.3f}" if (val % 1) != 0 else f"${int(val):,}"

    def format_units(val: float) -> str:
        if val == 0:
            return "0 units"
        return f"{val:,.3f} units" if (val % 1) != 0 else f"{int(val):,} units"

    metrics = {
        "💰 Max Risk Allowed": format_currency(risk_amount),
        "📦 Position Size": format_units(position_size),
        "🛑 Suggested Stop Loss": format_currency(suggested_stop),
        "💸 Capital Required": format_currency(capital_required),
        "🎯 Expected Reward": format_currency(expected_reward),
        "⚖️ Reward-to-Risk Ratio": f"{reward_to_risk:.2f}:1",
    }

    for label, val in metrics.items():
        st.metric(label=label, value=val)

    # Warnings
    if reward_to_risk < 2.0:
        st.warning("⚠️ Reward-to-risk ratio is below 2:1. Consider adjusting your target.")
    if capital_required > liquid_capital:
        st.error("🚫 This trade requires more capital than your liquid balance!")
    elif capital_required > 0.8 * liquid_capital:
        st.warning(
            "⚠️ This trade uses over 80% of your liquid capital. Consider reducing position size."
        )


# ────────────────────────────────────────────────────────────────────────────────
# 📢 Disclaimer
# ────────────────────────────────────────────────────────────────────────────────
def display_disclaimer():
    st.markdown("---")
    st.subheader("📢 Disclaimer")
    st.markdown(
        """
        **This tool is provided for educational purposes only** and does not constitute financial advice.

        Trading involves risk. Always consult a licensed financial advisor and only use capital you can afford to lose.
        """
    )
    if not st.checkbox("✅ I understand and accept the disclaimer."):
        st.warning("Please acknowledge the disclaimer to proceed.")
        st.stop()


# ────────────────────────────────────────────────────────────────────────────────
# 🚀 Main Application
# ────────────────────────────────────────────────────────────────────────────────
def main():
    setup_page()
    display_header()

    # Step 1: Get all eight user inputs, including a placeholder stop_loss_price
    (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
        stop_loss_price,
    ) = get_user_inputs()

    # Step 2: If the user never edited “Stop Loss Price,” it stays at 0.000 initially.
    #         We need to overwrite that with our “suggested_stop” (so it pre-fills properly).
    #         To do this, compute a suggested_stop here:
    #         (re-run the same portion of calculate_trade_metrics that produces suggested_stop)
    max_position_value = liquid_capital * leverage
    max_units = (max_position_value / entry_price) if entry_price > 0 else 0.0
    risk_amount = liquid_capital * (risk_percent / 100)
    required_risk_per_unit = (risk_amount / max_units) if max_units > 0 else 0.0
    suggested_stop = (
        entry_price - required_risk_per_unit if direction == "Long" else entry_price + required_risk_per_unit
    )
    suggested_stop = round(suggested_stop, 3)

    # If the user hasn’t typed anything different (stop_loss_price == 0.0),
    # force it to be our suggested_stop. Otherwise, respect their override.
    if stop_loss_price == 0.0:
        # Bypass Streamlit’s cache to forcibly reset the widget’s default:
        st.session_state["stop_loss_price"] = suggested_stop
        stop_loss_price = suggested_stop

    # Step 3: Now call calculate_trade_metrics(), feeding the user’s final stop_loss_price
    (
        _,
        position_size,
        _,
        capital_required,
        expected_reward,
        reward_to_risk,
    ) = calculate_trade_metrics(
        liquid_capital, risk_percent, entry_price, direction, target_price, leverage, stop_loss_price
    )

    # Step 4: Display results + warnings
    display_results(
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        liquid_capital,
    )

    # Step 5: Show the disclaimer at the bottom
    display_disclaimer()


if __name__ == "__main__":
    main()
