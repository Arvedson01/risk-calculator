import streamlit as st
from PIL import Image
from typing import Literal, Tuple

# Constants
DEFAULT_RISK_PERCENT = 1.000
MIN_LEVERAGE = 1.000
MIN_REWARD_RISK_RATIO = 2.000

# ────────────────────────────────────────────────────────────────────────────────
# 📄 Page Setup (must be the very first Streamlit call)
# ────────────────────────────────────────────────────────────────────────────────
def setup_page():
    """Configure page settings and clear cache."""
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
    """Display the logo (if available) and the title + brief description."""
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
        - 🛑 Calculate an optimal stop loss so that you risk precisely 1%  
        - 🎯 Show reward-to-risk based on your chosen target price  
        - 🧬 Factor in leverage to compute **capital required**  
        - ⚠️ Warn you if your capital or risk rules would be violated  
        """
    )


# ────────────────────────────────────────────────────────────────────────────────
# 📝 User Inputs
# ────────────────────────────────────────────────────────────────────────────────
def get_user_inputs() -> Tuple[
    float, float, float, float, Literal["Long", "Short"], float, float
]:
    """
    Collect and return all user inputs, using a 2-column layout.
    All numeric fields accept 3-decimals under the hood,
    but only show decimals if they are non-zero.
    """
    col1, col2 = st.columns(2, gap="small")

    with col1:
        total_capital = st.number_input(
            "💼 Total Capital ($)",
            min_value=0.000,
            value=10000.000,
            step=0.001,
            format="%g",
            help="Your total account size (for context).",
        )

        liquid_capital = st.number_input(
            "💧 Liquid Capital for Trading ($)",
            min_value=0.000,
            value=10000.000,
            step=0.001,
            format="%g",
            help="Only the cash you have available right now to take new trades.",
        )

        risk_percent = st.number_input(
            "⚠️ Risk % per trade",
            min_value=0.001,
            max_value=100.000,
            value=DEFAULT_RISK_PERCENT,
            step=0.001,
            format="%g",
            help="What percentage of your liquid capital do you want to risk?",
        )

    with col2:
        entry_price = st.number_input(
            "🎯 Entry Price ($)",
            min_value=0.001,
            value=100.000,
            step=0.001,
            format="%g",
            help="The price at which you plan to enter the trade.",
        )

        direction = st.radio(
            "📈 Are you going long or short?",
            ["Long", "Short"],
            horizontal=True,
            help="Choose Long if you expect price to rise, Short if you expect it to fall.",
        )

        target_price = st.number_input(
            "🎯 Target Price ($)",
            min_value=0.000,
            value=105.000,
            step=0.001,
            format="%g",
            help="Your profit-taking level. Used to compute reward/RR.",
        )

        leverage = st.number_input(
            "🪜 Leverage (e.g. 1 = no leverage)",
            min_value=MIN_LEVERAGE,
            value=1.000,
            step=0.001,
            format="%g",
            help="e.g. 1 = no leverage, 2 = 2×, 10 = 10×, etc.",
        )

    return (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
    )


# ────────────────────────────────────────────────────────────────────────────────
# 🧮 Core Calculations (Fixed)
# ────────────────────────────────────────────────────────────────────────────────
def calculate_trade_metrics(
    liquid_capital: float,
    risk_percent: float,
    entry_price: float,
    direction: Literal["Long", "Short"],
    target_price: float,
    leverage: float,
) -> Tuple[
    float,  # risk_amount
    float,  # position_size
    float,  # suggested_stop
    float,  # capital_required
    float,  # expected_reward
    float,  # reward_to_risk
    float,  # stop_loss_price
]:
    """
    Calculate all trade metrics based on user inputs:
    1) risk_amount (1% of liquid capital)
    2) max_units = (liquid_capital * leverage) / entry_price
    3) required_risk_per_unit = risk_amount / max_units
    4) suggested_stop = entry_price ± required_risk_per_unit (based on direction)
    5) user overrides stop_loss_price
    6) actual_risk_per_unit = |entry_price - stop_loss_price|
    7) final position_size = risk_amount / actual_risk_per_unit
    8) capital_required = (position_size * entry_price) / leverage
    9) reward metrics
    """
    # 1) Dollar amount you are risking
    risk_amount = liquid_capital * (risk_percent / 100)

    # 2) Theoretical max units if you used all available margin
    max_position_value = liquid_capital * leverage
    max_units = (max_position_value / entry_price) if entry_price > 0 else 0.0

    # 3) How much price move per unit corresponds to exactly risk_amount
    required_risk_per_unit = (risk_amount / max_units) if max_units > 0 else 0.0

    # 4) Suggest a stop that is ± required_risk_per_unit
    if direction == "Long":
        suggested_stop = entry_price - required_risk_per_unit
    else:  # Short
        suggested_stop = entry_price + required_risk_per_unit

    # 5) Let the user override the suggested stop
    stop_loss_price = st.number_input(
        "🛑 Stop Loss Price ($)",
        min_value=0.000,
        value=round(suggested_stop, 3),
        step=0.001,
        format="%g",
        help="If you want a different stop‐loss than the suggestion, edit here.",
    )

    # 6) Recompute actual risk per unit
    actual_risk_per_unit = (
        abs(entry_price - stop_loss_price)
        if stop_loss_price != entry_price
        else 0.0
    )

    # 7) Position size that risks exactly risk_amount
    position_size = (
        (risk_amount / actual_risk_per_unit) if actual_risk_per_unit > 0 else 0.0
    )

    # 8) Capital required, factoring in leverage
    position_value = position_size * entry_price
    capital_required = (position_value / leverage) if leverage > 0 else 0.0

    # 9) Reward calculations
    reward_per_unit = abs(target_price - entry_price)
    expected_reward = reward_per_unit * position_size
    reward_to_risk = (
        (expected_reward / risk_amount) if risk_amount > 0 else 0.0
    )

    return (
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        stop_loss_price,
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
    """Display the trade summary (metrics + warnings)."""
    st.subheader("📈 Trade Summary")

    # Formatting helpers:
    def format_currency(value: float) -> str:
        if abs(value) < 0.001:
            return "$0.000"
        return f"${value:,.3f}" if (value % 1) != 0 else f"${int(value):,}"

    def format_units(value: float) -> str:
        if value == 0:
            return "0 units"
        return f"{value:,.3f} units" if (value % 1) != 0 else f"{int(value):,} units"

    # Build the metrics dictionary for display
    metrics = {
        "💰 Max Risk Allowed": format_currency(risk_amount),
        "📦 Position Size": format_units(position_size),
        "🛑 Suggested Stop Loss": format_currency(suggested_stop),
        "💸 Capital Required": format_currency(capital_required),
        "🎯 Expected Reward": format_currency(expected_reward),
        "⚖️ Reward‐to‐Risk Ratio": f"{reward_to_risk:.2f}:1",
    }

    # Render each metric as a st.metric
    for label, value in metrics.items():
        st.metric(label=label, value=value)

    # Warnings if any
    if reward_to_risk < MIN_REWARD_RISK_RATIO:
        st.warning(
            f"⚠️ Reward‐to‐risk ratio is below {MIN_REWARD_RISK_RATIO:.0f}:1. "
            "Consider adjusting your target or stop."
        )

    if capital_required > liquid_capital:
        st.error("🚫 This trade requires more capital than your liquid balance!")
    elif capital_required > 0.8 * liquid_capital:
        st.warning(
            "⚠️ This trade uses over 80% of your liquid capital. "
            "Consider reducing position size."
        )


# ────────────────────────────────────────────────────────────────────────────────
# 📢 Disclaimer
# ────────────────────────────────────────────────────────────────────────────────
def display_disclaimer():
    """Show disclaimer and halt if user has not acknowledged."""
    st.markdown("---")
    st.subheader("📢 Disclaimer")
    st.markdown(
        """
        **This tool is provided for educational purposes only** and 
        does not constitute financial advice.

        Trading involves substantial risk. Consult a licensed financial advisor 
        and only trade with capital you can afford to lose.
        """
    )

    if not st.checkbox("✅ I understand and accept the disclaimer."):
        st.warning("Please acknowledge the disclaimer to proceed.")
        st.stop()


# ────────────────────────────────────────────────────────────────────────────────
# 🚀 Main Application
# ────────────────────────────────────────────────────────────────────────────────
def main():
    # 1) Page setup (must be first Streamlit call)
    setup_page()

    # 2) Header + logo + description
    display_header()

    # 3) Collect inputs
    (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
    ) = get_user_inputs()

    # 4) Compute all metrics
    (
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        stop_loss_price,
    ) = calculate_trade_metrics(
        liquid_capital, risk_percent, entry_price, direction, target_price, leverage
    )

    # 5) Display results + warnings
    display_results(
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        liquid_capital,
    )

    # 6) Disclaimer & user acknowledgment check
    display_disclaimer()


if __name__ == "__main__":
    main()
