import streamlit as st
from PIL import Image
from typing import Literal, Tuple

# ────────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────────
DEFAULT_RISK_PERCENT = 1.000
MIN_LEVERAGE = 1.000
MIN_REWARD_RISK_RATIO = 2.000


# ────────────────────────────────────────────────────────────────────────────────
# 📄 Page Setup (must be the very first Streamlit call in your script)
# ────────────────────────────────────────────────────────────────────────────────
def setup_page():
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
    """
    Show a logo (if it exists) plus the app title and a short bullet list.
    """
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
        - 🛑 Calculate an optimal stop‐loss to risk precisely 1%  
        - 🎯 Show reward‐to‐risk based on your chosen target price  
        - 🧬 Factor in leverage to compute **capital required**  
        - ⚠️ Warn if your capital or risk rules would be violated  
        """
    )


# ────────────────────────────────────────────────────────────────────────────────
# 📝 User Inputs
# ────────────────────────────────────────────────────────────────────────────────
def get_user_inputs() -> Tuple[
    float, float, float, float, Literal["Long", "Short"], float, float
]:
    """
    Collect and return:
      - total_capital
      - liquid_capital
      - risk_percent
      - entry_price
      - direction (Long/Short)
      - target_price
      - leverage
    (We compute suggested_stop separately and supply it to the Stop Loss widget below.)
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
            value=DEFAULT_RISK_PERCENT,
            step=0.001,
            format="%g",
            key="risk_pct",
        )
        leverage = st.number_input(
            "🧬 Leverage (e.g. 1 = no leverage)",
            min_value=MIN_LEVERAGE,
            value=MIN_LEVERAGE,
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
        # We leave Stop Loss out here; we’ll insert it later once we know "suggested_stop"

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
    Steps:
      1) risk_amount = liquid_capital * (risk_percent / 100)
      2) max_units = (liquid_capital * leverage) / entry_price
      3) required_risk_per_unit = risk_amount / max_units
      4) suggested_stop = entry_price ± required_risk_per_unit (based on direction)
      5) actual_risk_per_unit = |entry_price - stop_loss_price|
      6) position_size = risk_amount / actual_risk_per_unit
      7) position_value = position_size * entry_price
      8) capital_required = position_value / leverage
      9) expected_reward & reward_to_risk
    """
    # 1) Dollar amount you’re risking
    risk_amount = liquid_capital * (risk_percent / 100)

    # 2) Theoretical max units if you used all margin
    max_position_value = liquid_capital * leverage
    max_units = (max_position_value / entry_price) if entry_price > 0 else 0.0

    # 3) Required risk per unit to risk EXACTLY risk_amount
    required_risk_per_unit = (risk_amount / max_units) if max_units > 0 else 0.0

    # 4) Suggested stop
    if direction == "Long":
        suggested_stop = entry_price - required_risk_per_unit
    else:  # "Short"
        suggested_stop = entry_price + required_risk_per_unit

    suggested_stop = round(suggested_stop, 3)

    # 5) Actual risk per unit (user‐entered stop_loss_price)
    actual_risk_per_unit = abs(entry_price - stop_loss_price) if stop_loss_price != entry_price else 0.0

    # 6) Final position size that risks exactly risk_amount
    position_size = (risk_amount / actual_risk_per_unit) if actual_risk_per_unit > 0 else 0.0

    # 7) Capital required (taking leverage into account)
    position_value = position_size * entry_price
    capital_required = (position_value / leverage) if leverage > 0 else 0.0

    # 8) Reward calculations
    reward_per_unit = abs(target_price - entry_price)
    expected_reward = reward_per_unit * position_size
    reward_to_risk = (expected_reward / risk_amount) if risk_amount > 0 else 0.0

    return (
        risk_amount,
        position_size,
        suggested_stop,
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
    """Show the Trade Summary metrics and any warnings."""
    st.subheader("📈 Trade Summary")

    def format_currency(val: float) -> str:
        if abs(val) < 0.001:
            return "$0.000"
        # Show 3 decimals if any fractional part, otherwise whole number
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
    if reward_to_risk < MIN_REWARD_RISK_RATIO:
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

    # 1️⃣ First, collect everything except Stop Loss
    (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
    ) = get_user_inputs()

    # 2️⃣ Compute “suggested_stop” so we can pre-fill that Stop Loss field.
    #     We re‐compute just Steps 1–4 from calculate_trade_metrics().
    risk_amount = liquid_capital * (risk_percent / 100)
    max_position_value = liquid_capital * leverage
    max_units = (max_position_value / entry_price) if entry_price > 0 else 0.0
    required_risk_per_unit = (risk_amount / max_units) if max_units > 0 else 0.0
    if direction == "Long":
        suggested_stop = entry_price - required_risk_per_unit
    else:
        suggested_stop = entry_price + required_risk_per_unit
    suggested_stop = round(suggested_stop, 3)

    # 3️⃣ Now show the Stop Loss input with default = suggested_stop
    stop_loss_price = st.number_input(
        "🛑 Stop Loss Price ($)",
        min_value=0.000,
        value=suggested_stop,
        step=0.001,
        format="%g",
        key="stop_loss_price",
        help="This field is pre‐filled with the suggested stop‐loss; you may override it.",
    )

    # 4️⃣ Run the full calculation, passing in the final stop_loss_price
    (
        risk_amount,
        position_size,
        suggested_stop,   # we already computed above, but return it anyway
        capital_required,
        expected_reward,
        reward_to_risk,
    ) = calculate_trade_metrics(
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
        stop_loss_price,
    )

    # 5️⃣ Show results + warnings
    display_results(
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        liquid_capital,
    )

    # 6️⃣ Show the disclaimer at the very bottom
    display_disclaimer()


if __name__ == "__main__":
    main()
