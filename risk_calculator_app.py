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

    # ─── Custom CSS Styling ──────────────────────────────────────────────────────
    st.markdown(
        """
        <style>
            /* Improve spacing between input widgets */
            .stNumberInput, .stRadio, .stCheckbox {
                margin-bottom: 1rem;
            }
            
            /* Style metric cards */
            .stMetric {
                background-color: #0E1117;
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
                margin: 0.25rem 0;
            }
            
            /* Style warning and error boxes */
            .stWarning, .stError {
                border-radius: 0.5rem;
                padding: 0.75rem 1rem;
            }
            
            /* Section headers (e.g. subheaders) */
            .stMarkdown h2 {
                border-bottom: 1px solid #2b3138;
                padding-bottom: 0.3rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────────────────────────
# 🖼️ Logo and Header
# ────────────────────────────────────────────────────────────────────────────────
def display_header(logo_path: str = "logo.png"):
    """
    Display a logo (if present) and the app title, plus an expandable
    “How to use this calculator” section.
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

    with st.expander("✨ How to use this calculator", expanded=True):
        st.markdown(
            """
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
    """
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("#### Capital Settings")
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
            value=1.000,
            step=0.001,
            format="%g",
            key="leverage",
        )

    with col2:
        st.markdown("#### Trade Settings")
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
        # Stop Loss will be inserted after suggested_stop is computed

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
    """Show the Trade Summary metrics and warnings in two columns."""
    st.subheader("📈 Trade Summary")

    def format_currency(val: float) -> str:
        if abs(val) < 0.001:
            return "$0.000"
        return f"${val:,.3f}" if (val % 1) != 0 else f"${int(val):,}"

    def format_units(val: float) -> str:
        if val == 0:
            return "0 units"
        return f"{val:,.3f} units" if (val % 1) != 0 else f"{int(val):,} units"

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.metric(label="💰 Max Risk Allowed", value=format_currency(risk_amount))
        st.metric(label="📦 Position Size", value=format_units(position_size))
        st.metric(label="🛑 Suggested Stop Loss", value=format_currency(suggested_stop))
    with col2:
        st.metric(label="💸 Capital Required", value=format_currency(capital_required))
        st.metric(label="🎯 Expected Reward", value=format_currency(expected_reward))
        st.metric(label="⚖️ Reward-to-Risk Ratio", value=f"{reward_to_risk:.2f}:1")

    # ─── Warnings section in an expander ────────────────────────────────────────
    if (reward_to_risk < MIN_REWARD_RISK_RATIO) or (capital_required > 0.8 * liquid_capital):
        with st.expander("⚠️ Risk Notices", expanded=True):
            if reward_to_risk < MIN_REWARD_RISK_RATIO:
                st.warning(
                    f"⚠️ Reward-to-risk ratio is below {MIN_REWARD_RISK_RATIO:.0f}:1. "
                    "Consider adjusting your target."
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
    """
    Right-align the disclaimer checkbox by using two columns,
    then call st.stop() if not acknowledged.
    """
    st.markdown("---")
    st.subheader("📢 Disclaimer")
    st.markdown(
        """
        **This tool is provided for educational purposes only** and does not constitute financial advice.

        Trading involves risk. Always consult a licensed financial advisor and only use capital you can afford to lose.
        """
    )
    col1, col2 = st.columns([3, 1], gap="small")
    with col2:
        if not st.checkbox("✅ I understand and accept the disclaimer"):
            st.warning("Please acknowledge the disclaimer to proceed.")
            st.stop()


# ────────────────────────────────────────────────────────────────────────────────
# 🚀 Main Application
# ────────────────────────────────────────────────────────────────────────────────
def main():
    setup_page()
    display_header()

    # 1️⃣ Gather inputs (except Stop Loss)
    (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
    ) = get_user_inputs()

    # 2️⃣ Compute “suggested_stop” so Stop Loss can be pre-filled
    risk_amount = liquid_capital * (risk_percent / 100)
    max_position_value = liquid_capital * leverage
    max_units = (max_position_value / entry_price) if entry_price > 0 else 0.0
    required_risk_per_unit = (risk_amount / max_units) if max_units > 0 else 0.0
    if direction == "Long":
        suggested_stop = entry_price - required_risk_per_unit
    else:
        suggested_stop = entry_price + required_risk_per_unit
    suggested_stop = round(suggested_stop, 3)

    # 3️⃣ Now show the Stop Loss widget (pre-filled with suggested_stop)
    stop_loss_price = st.number_input(
        "🛑 Stop Loss Price ($)",
        min_value=0.000,
        value=suggested_stop,
        step=0.001,
        format="%g",
        key="stop_loss_price",
        help="Pre‐filled with the suggested stop‐loss; you may override it.",
    )

    # 4️⃣ Perform full trade calculations
    (
        risk_amount,
        position_size,
        suggested_stop,    # recomputed but matches earlier
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

    # 5️⃣ Display results + warnings
    display_results(
        risk_amount,
        position_size,
        suggested_stop,
        capital_required,
        expected_reward,
        reward_to_risk,
        liquid_capital,
    )

    # 6️⃣ Show disclaimer at the bottom
    display_disclaimer()


if __name__ == "__main__":
    main()
