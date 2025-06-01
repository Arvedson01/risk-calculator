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
# 📄 Page Setup (must be the very first Streamlit call)
# ────────────────────────────────────────────────────────────────────────────────
def setup_page():
    st.set_page_config(
        page_title="1% Risk Calculator",
        page_icon="📊",
        layout="centered"
    )
    st.cache_data.clear()

    # ─── 1. Themed Custom CSS with Subtle Animations ─────────────────────────────────
    st.markdown(
        """
        <style>
            /*── General Spacing Improvements ─────────────────────────────────────────*/
            .stNumberInput, .stRadio, .stCheckbox {
                margin-bottom: 1.25rem; /* Slightly more vertical space */
                transition: all 0.2s ease-in-out; /* Smooth transition for interaction */
            }
            .stNumberInput > div > div > input:focus,
            .stRadio > div > label:hover,
            .stCheckbox > label:hover {
                box-shadow: 0 0 0 2px #BB86FC; /* Highlight on focus/hover */
                border-color: #BB86FC;
            }

            /*── Enhanced Metric Cards ────────────────────────────────────────────────*/
            .stMetric {
                background-color: #1A1A2E;    /* Darker, richer background */
                border-radius: 0.75rem;       /* Softer rounded corners */
                padding: 0.75rem 1.25rem;     /* More padding */
                margin: 0.4rem 0;             /* Adjusted vertical margin */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); /* Subtle shadow for depth */
                transition: transform 0.2s ease-in-out;   /* Smooth hover effect */
            }
            .stMetric:hover {
                transform: translateY(-3px); /* Lifts card on hover */
            }

            /*── Prominent Warning/Error Boxes ───────────────────────────────────────*/
            .stWarning, .stError {
                background-color: #332B00;           /* Darker warning background */
                border-left: 5px solid #FFD700;      /* Gold left border for warnings */
                border-radius: 0.6rem;
                padding: 1rem 1.25rem;
                margin-top: 1.5rem;                  /* More space above warnings */
                margin-bottom: 1.5rem;
            }
            .stError {
                background-color: #330000;           /* Darker error background */
                border-left-color: #FF6347;          /* Tomato red left border for errors */
            }

            /*── Distinct Section Headers (h2) ────────────────────────────────────────*/
            .stMarkdown h2 {
                color: #90CAF9;                     /* Lighter blue for headers */
                border-bottom: 2px solid #2b3138;   /* Slightly thicker border */
                padding-bottom: 0.5rem;
                margin-top: 2rem;                   /* More space above headers */
                margin-bottom: 1.5rem;
                font-size: 1.8em;                   /* Larger font size */
                animation: fadeInSlideUp 0.8s ease-out forwards; /* Subtle entrance */
            }

            /*── Main Title Animation (h1) ───────────────────────────────────────────*/
            .stApp h1 {
                animation: fadeInSlideUp 0.8s ease-out forwards;
                text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5); /* Subtle shadow for depth */
            }

            /*── Subheaders for input groups (h4) ────────────────────────────────────*/
            .stMarkdown h4 {
                color: #BB86FC;                     /* Purple for subheaders */
                margin-top: 1.5rem;
                margin-bottom: 0.8rem;
                font-size: 1.2em;
                border-bottom: 1px dashed #3A3A50;  /* Dashed subtle border */
                padding-bottom: 0.3rem;
            }

            /*── Expander styling ────────────────────────────────────────────────────*/
            .streamlit-expanderHeader {
                background-color: #28283D; /* Darker background for expander header */
                border-radius: 0.5rem;
                padding: 0.75rem 1rem;
                font-weight: bold;
                color: #E0E0E0;            /* Lighter text for expander header */
            }
            .streamlit-expanderContent {
                background-color: #1A1A2E; /* Matches metric card background */
                border-bottom-left-radius: 0.75rem;
                border-bottom-right-radius: 0.75rem;
                padding: 1rem;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
            }

            /*── Title entrance animation ─────────────────────────────────────────────*/
            @keyframes fadeInSlideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
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
    Show logo (if found) and the bold app title (with entrance animation),
    plus an expander explaining how to use the calculator.
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

    # ─── 2. Enhanced Header with Expander ───────────────────────────────────────
    with st.expander("✨ How to Use This Calculator", expanded=True):
        st.markdown(
            """
            - 💰 Risk exactly **1%** of your **liquid capital** per trade.  
            - 📉 Calculate an optimal **stop-loss** to precisely risk 1%.  
            - 📈 See your **reward-to-risk** ratio based on your chosen target price.  
            - 🔗 Factor in **leverage** to compute the **capital required**.  
            - ⚠️ Get **alerts** if your capital or risk rules are violated.  
            """
        )


# ────────────────────────────────────────────────────────────────────────────────
# 📝 User Inputs
# ────────────────────────────────────────────────────────────────────────────────
def get_user_inputs() -> Tuple[
    float,  # total_capital
    float,  # liquid_capital
    float,  # risk_percent
    float,  # entry_price
    Literal["Long", "Short"],  # direction
    float,  # target_price
    float,  # leverage
]:
    """
    Gather user inputs and return them. Grouped under subheaders styled by CSS.
    """
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("#### 🏦 Capital Settings")
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
        st.markdown("#### 📊 Trade Settings")
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

        # Stop Loss is inserted after suggested_stop is computed

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

    # 2) Theoretical max units if you used 100% margin
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

    # 5) Actual risk per unit, based on user-entered stop_loss_price
    actual_risk_per_unit = abs(entry_price - stop_loss_price) if stop_loss_price != entry_price else 0.0

    # 6) Final position size that risks exactly risk_amount
    position_size = (risk_amount / actual_risk_per_unit) if actual_risk_per_unit > 0 else 0.0

    # 7) Compute position_value
    position_value = position_size * entry_price

    # 8) Capital required (accounting for leverage)
    capital_required = (position_value / leverage) if leverage > 0 else 0.0

    # 9) Reward calculations
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
    """
    Show the trade summary in two columns, preceded by a divider,
    then put any warnings inside an expander.
    """
    st.markdown("---")  # 3. Divider before Trade Summary
    st.subheader("📈 Trade Summary")

    def format_currency(val: float) -> str:
        # Hide “.000” if it’s a whole number; show .xxx only if needed
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

    # ─── 5. Organize Warnings within an Expander ─────────────────────────────────
    if (
        reward_to_risk < MIN_REWARD_RISK_RATIO
        or capital_required > 0.8 * liquid_capital
    ):
        with st.expander("⚠️ Risk Notices", expanded=True):
            if reward_to_risk < MIN_REWARD_RISK_RATIO:
                st.warning(
                    f"⚠️ Reward-to-risk ratio (**{reward_to_risk:.2f}:1**) is below "
                    f"**{MIN_REWARD_RISK_RATIO}:1**. Consider adjusting your target."
                )
            if capital_required > liquid_capital:
                st.error(
                    f"🚫 Required capital (**{format_currency(capital_required)}**) "
                    f"exceeds your liquid capital (**{format_currency(liquid_capital)}**)."
                )
            elif capital_required > 0.8 * liquid_capital:
                st.warning(
                    f"⚠️ Trade uses more than **80%** of your liquid capital "
                    f"(**{format_currency(capital_required)}** > 80% of **{format_currency(liquid_capital)}**)."
                )


# ────────────────────────────────────────────────────────────────────────────────
# 📢 Disclaimer
# ────────────────────────────────────────────────────────────────────────────────
def display_disclaimer():
    """
    Right-align the checkbox by splitting into two columns,
    and use st.info instead of st.warning for the prompt if unchecked.
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
        if not st.checkbox(
            "✅ I understand and accept the disclaimer", key="disclaimer_checkbox"
        ):
            st.info("Please acknowledge the disclaimer to proceed.")
            st.stop()


# ────────────────────────────────────────────────────────────────────────────────
# 📜 Footer
# ────────────────────────────────────────────────────────────────────────────────
def display_footer():
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #7F8C8D; font-size: 0.8em;'>"
        "© 2025 1% Risk Calculator. For educational use only."
        "</p>",
        unsafe_allow_html=True
    )


# ────────────────────────────────────────────────────────────────────────────────
# 🚀 Main Application
# ────────────────────────────────────────────────────────────────────────────────
def main():
    setup_page()
    display_header()

    # 1️⃣ Gather inputs (excluding Stop Loss)
    (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
    ) = get_user_inputs()

    # 2️⃣ Precompute suggested_stop to pre-fill the Stop Loss widget
    risk_amount = liquid_capital * (risk_percent / 100)
    max_position_value = liquid_capital * leverage
    max_units = (max_position_value / entry_price) if entry_price > 0 else 0.0
    required_risk_per_unit = (risk_amount / max_units) if max_units > 0 else 0.0
    if direction == "Long":
        suggested_stop = entry_price - required_risk_per_unit
    else:
        suggested_stop = entry_price + required_risk_per_unit
    suggested_stop = round(suggested_stop, 3)

    # 3️⃣ Show the Stop Loss widget (pre-filled with suggested_stop, with 🛑 icon)
    stop_loss_price = st.number_input(
        "🛑 Stop Loss Price ($)",
        min_value=0.000,
        value=suggested_stop,
        step=0.001,
        format="%g",
        key="stop_loss_price",
        help="Pre-filled with suggested stop-loss; override as needed.",
    )

    # 4️⃣ Perform full trade calculations
    (
        risk_amount,
        position_size,
        suggested_stop,    # Should match above
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

    # 6️⃣ Show disclaimer at the bottom
    display_disclaimer()

    # 7️⃣ Show footer
    display_footer()


if __name__ == "__main__":
    main()
