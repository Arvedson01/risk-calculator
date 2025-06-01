import streamlit as st
from PIL import Image
from typing import Literal, Tuple
import logging

# ────────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────────
DEFAULT_RISK_PERCENT = 1.000
MIN_LEVERAGE = 1.000
MAX_LEVERAGE_WARNING = 10.000  # Threshold for high leverage warning
MIN_REWARD_RISK_RATIO = 2.000
DEFAULT_SLIPPAGE = 0.100  # 0.1% more realistic for crypto

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            /*── Global Styling (Body Background) ──────────────────────────────────*/
            body {
                /* A subtle, dark geometric pattern for a futuristic feel */
                background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92B3' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zm0 40v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0 12v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm-30 0v-4h-2v4H0v2h4v4h2v-4h4v-2H6zm0-40V0h-2v4H0v2h4v4h2V6h4V4H6zm0 12v-4h-2v4H0v2h4v4h2v-4h4v-2H6zm0 12v-4h-2v4H0v2h4v4h2v-4h4v-2H6zm30-12v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zM24 2c3.314 0 6 2.686 6 6s-2.686 6-6 6-6-2.686-6-6 2.686-6 6-6zm0 40c3.314 0 6 2.686 6 6s-2.686 6-6 6-6-2.686-6-6 2.686-6 6-6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
                background-color: #0F0F1A; /* Even darker base background */
            }

            /*── General Spacing Improvements ─────────────────────────────────────────*/
            .stNumberInput, .stRadio, .stCheckbox {
                margin-bottom: 1.25rem; /* Slightly more vertical space */
                transition: all 0.2s ease-in-out; /* Smooth transition for interaction */
            }

            /*── Number Input Specifics (Digital Readout Look) ────────────────────────*/
            .stNumberInput > div > div > input {
                font-family: 'Space Mono', monospace; /* Digital font */
                background-color: #1A1A2E; /* Darker input background */
                border: 1px solid #3A3A50; /* Subtle border */
                border-radius: 0.5rem;
                padding: 0.75rem 1rem;
                color: #00FFC0; /* Neon green text for values */
                transition: all 0.3s ease-in-out;
            }
            .stNumberInput > div > div > input:focus {
                box-shadow: 0 0 0 2px #BB86FC, 0 0 10px #BB86FC; /* Highlight with glow on focus */
                border-color: #BB86FC;
            }

            /*── Radio Button (Long/Short) as Toggle ──────────────────────────────────*/
            .stRadio > label {
                background-color: #28283D;
                border-radius: 0.75rem;
                padding: 0.5rem 0.75rem;
                margin-right: 0.5rem; /* Space between options */
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
                color: #E0E0E0;
            }
            .stRadio > label:hover {
                background-color: #3A3A50;
                transform: translateY(-2px);
            }
            /* Style for the actual radio input (hidden) */
            .stRadio > label > input[type="radio"] {
                display: none;
            }
            /* Style for selected radio option */
            .stRadio > label > input[type="radio"]:checked + div {
                background-color: transparent; /* Remove default radio dot */
            }
            .stRadio > label > input[type="radio"]:checked + div > p {
                /* Apply color to the text of the selected option */
                color: #00FFC0; /* Default selected color */
            }
            /* Specific colors for Long/Short selection */
            .stRadio > div > label:nth-of-type(1) input[type="radio"]:checked + div p {
                color: #00FF80; /* Green for Long */
            }
            .stRadio > div > label:nth-of-type(2) input[type="radio"]:checked + div p {
                color: #FF6347; /* Red for Short */
            }


            /*── Checkbox Hover ───────────────────────────────────────────────────────*/
            .stCheckbox > label:hover {
                box-shadow: 0 0 0 2px #BB86FC; /* Highlight on hover */
                border-color: #BB86FC;
            }

            /*── Enhanced Metric Cards (Subtle Glow) ──────────────────────────────────*/
            .stMetric {
                background-color: #1A1A2E;     /* Darker, richer background */
                border-radius: 0.75rem;        /* Softer rounded corners */
                padding: 0.75rem 1.25rem;      /* More padding */
                margin: 0.4rem 0;              /* Adjusted vertical margin */
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 5px rgba(187, 134, 252, 0.2); /* Subtle glow */
                transition: transform 0.2s ease-in-out, box-shadow 0.3s ease; /* Smooth hover effect */
                border: 1px solid #28283D; /* Slight border for definition */
            }
            .stMetric:hover {
                transform: translateY(-3px); /* Lifts card on hover */
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6), 0 0 15px rgba(187, 134, 252, 0.4); /* Stronger glow on hover */
            }
            .stMetric > div[data-testid="stMetricValue"] {
                color: #00FFC0; /* Neon green for metric values */
                font-family: 'Space Mono', monospace;
                font-size: 1.7em; /* Slightly larger value */
            }
            .stMetric > div[data-testid="stMetricLabel"] label {
                color: #90CAF9; /* Lighter blue for labels */
                font-size: 0.9em;
            }


            /*── Prominent Warning/Error Boxes (More Dramatic) ───────────────────────*/
            .stWarning, .stError {
                background-color: #262100;     /* Darker, more intense warning background */
                border-left: 6px solid #FFD700; /* Thicker, brighter gold left border */
                border-radius: 0.6rem;
                padding: 1.2rem 1.5rem;
                margin-top: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4), 0 0 8px rgba(255, 215, 0, 0.3); /* Warning glow */
            }
            .stError {
                background-color: #260000;     /* Darker, more intense error background */
                border-left-color: #FF4747;    /* Brighter, more aggressive red for errors */
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4), 0 0 8px rgba(255, 71, 71, 0.4); /* Error glow */
            }
            /* Bold important text within warnings/errors */
            .stWarning p strong, .stError p strong {
                color: inherit; /* Keep existing text color */
                text-shadow: 0 0 5px rgba(255, 255, 255, 0.5); /* Subtle text glow */
            }


            /*── Distinct Section Headers (h2) ────────────────────────────────────────*/
            .stMarkdown h2 {
                color: #90CAF9;                /* Lighter blue for headers */
                border-bottom: 2px solid #2b3138; /* Slightly thicker border */
                padding-bottom: 0.5rem;
                margin-top: 2rem;
                margin-bottom: 1.5rem;
                font-size: 1.8em;
            }

            /*── Main Title Animation (h1) with Glow ────────────────────────────────*/
            .stApp h1 {
                animation: fadeInSlideUp 0.8s ease-out forwards;
                text-shadow: 0 0 10px #BB86FC, 0 0 20px #BB86FC; /* Prominent glow */
                color: #BB86FC; /* Matches glow color */
            }

            /*── Subheaders for input groups (h4) as Panels ──────────────────────────*/
            .stMarkdown h4 {
                color: #BB86FC;                /* Purple for subheaders */
                margin-top: 1.5rem;
                margin-bottom: 0.8rem;
                font-size: 1.2em;
                border-bottom: none; /* Remove previous dashed border */
                padding-bottom: 0;

                /* Panel Styling */
                background-color: #151525; /* Slightly darker than main background */
                border: 1px solid #28283D;
                border-radius: 0.75rem;
                padding: 1rem 1.25rem;
                box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.4), 0 0 5px rgba(187, 134, 252, 0.1); /* Inset shadow for depth, subtle outer glow */
            }

            /* Apply panel styling to the direct parent of h4 for full section */
            .stMarkdown h4 + div { /* Selects the div immediately following an h4 */
                background-color: #1A1A2E; /* Matches metric card background */
                border-bottom-left-radius: 0.75rem;
                border-bottom-right-radius: 0.75rem;
                border: 1px solid #28283D;
                border-top: none; /* Blend with the h4 panel above */
                padding: 1rem 1.25rem 2rem; /* More padding at bottom of section */
                margin-top: -0.8rem; /* Pull up to join h4 */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); /* Outer shadow for the full panel */
            }


            /*── Expander styling ────────────────────────────────────────────────────*/
            .streamlit-expanderHeader {
                background-color: #28283D; /* Darker background for expander header */
                border-radius: 0.5rem;
                padding: 0.75rem 1rem;
                font-weight: bold;
                color: #E0E0E0;             /* Lighter text for expander header */
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3); /* Subtle shadow for expander */
            }
            .streamlit-expanderContent {
                background-color: #1A1A2E; /* Matches metric card background */
                border-bottom-left-radius: 0.75rem;
                border-bottom-right-radius: 0.75rem;
                padding: 1rem;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
                border: 1px solid #28283D; /* Add border for content */
                border-top: none;
            }

            /*── Title entrance animation ─────────────────────────────────────────────*/
            @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
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
            st.title("📊 1% Risk Management Calculator (Quantum Ledger)")
    except FileNotFoundError:
        logger.warning("Logo image not found, using default header")
        st.title("📊 1% Risk Management Calculator (Quantum Ledger)")

    # How-to guide expander
    with st.expander("✨ How to Use This Calculator", expanded=True):
        st.markdown(
            """
            - 💰 Risk exactly **1%** of your **liquid capital** per trade  
            - 📉 Calculate an optimal **stop-loss** to precisely risk 1%  
            - 📈 See your **reward-to-risk** ratio based on your chosen target price  
            - 🔗 Factor in **leverage** to compute the **capital required**  
            - ⚠️ Get **alerts** if your capital or risk rules are violated  
            """
        )


# ────────────────────────────────────────────────────────────────────────────────
# 📝 User Inputs
# ────────────────────────────────────────────────────────────────────────────────
def get_user_inputs() -> Tuple[
    float, float, float, float, Literal["Long", "Short"], float, float, float, bool, float, float
]:
    """Gather user inputs with improved validation and defaults."""
    col1, col2 = st.columns(2, gap="medium")

    # Panel for Capital Settings
    with col1:
        st.markdown("<h4>🏦 Capital Settings</h4>", unsafe_allow_html=True)
        st.markdown("<div>", unsafe_allow_html=True)
        
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
            help="Higher leverage increases both potential gains and losses"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Panel for Trade Settings
    with col2:
        st.markdown("<h4>📊 Trade Settings</h4>", unsafe_allow_html=True)
        st.markdown("<div>", unsafe_allow_html=True)
        
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

        slippage_pct = st.number_input(
            "📉 Estimated Slippage (%)",
            min_value=0.000,
            value=DEFAULT_SLIPPAGE,
            step=0.001,
            format="%g",
            key="slippage_pct",
            help="Typical values: 0.1% for crypto, 0.05% for liquid stocks"
        ) / 100  # Convert to decimal
        
        st.markdown("</div>", unsafe_allow_html=True)

    # ATR Settings Panel
    st.markdown("<h4 style='margin-top: 2rem;'>📊 Volatility-Based Stops (ATR)</h4>", unsafe_allow_html=True)
    st.markdown("<div>", unsafe_allow_html=True)
    
    use_atr = st.checkbox(
        "🔍 Use ATR-Based Stop Loss (Recommended for Volatile Assets)",
        value=False,
        key="use_atr",
        help="[How to find ATR on TradingView](https://www.tradingview.com/support/solutions/43000502348-average-true-range-atr/)"
    )

    atr_value = 0.0
    atr_multiplier = 0.0

    if use_atr:
        atr_help = """
        **ATR Guide:**  
        - Find ATR(14) on your charting platform (e.g., TradingView)  
        - Common periods: 14 bars (days/hours)  
        - Typical values: 2.5 for stocks, 50-200 for crypto  
        """
        st.markdown(atr_help)
        
        atr_value = st.number_input(
            "📈 Average True Range (ATR) Value",
            min_value=0.000,
            value=0.000,
            step=0.001,
            format="%g",
            key="atr_value",
        )
        
        if use_atr and atr_value <= 0:
            st.warning("⚠️ ATR value must be positive when ATR is enabled")
        
        atr_multiplier = st.number_input(
            "✖️ ATR Multiplier",
            min_value=0.1,
            value=1.5,
            step=0.1,
            format="%g",
            key="atr_multiplier",
            help="1.5-2.0 for day trading, 2.0-3.0 for swing trading"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    return (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
        slippage_pct,
        use_atr,
        atr_value,
        atr_multiplier
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
    slippage_pct: float,
) -> Tuple[float, float, float, float, float, float]:
    """Enhanced calculations with rounding and leverage checks."""
    # Validate entry price
    if entry_price <= 0:
        st.error("Entry price must be positive.")
        st.stop()

    # 1) Dollar amount you're risking
    risk_amount = liquid_capital * (risk_percent / 100)

    # 2) Calculate effective stop loss with slippage
    effective_stop_loss = stop_loss_price
    if slippage_pct > 0:
        if direction == "Long":
            effective_stop_loss = stop_loss_price * (1 - slippage_pct)
        else:  # "Short"
            effective_stop_loss = stop_loss_price * (1 + slippage_pct)

    # Validate stop loss
    if direction == "Long" and effective_stop_loss >= entry_price:
        st.error("🚫 For Long trades, Stop Loss must be below Entry Price (accounting for slippage).")
        st.stop()
    if direction == "Short" and effective_stop_loss <= entry_price:
        st.error("🚫 For Short trades, Stop Loss must be above Entry Price (accounting for slippage).")
        st.stop()

    # Calculate actual risk per unit
    actual_risk_per_unit = abs(entry_price - effective_stop_loss)
    if actual_risk_per_unit == 0:
        st.error("Stop Loss too close to Entry Price. Adjust your stop or slippage.")
        st.stop()

    # Position size (rounded to 3 decimal places for crypto)
    position_size = round(risk_amount / actual_risk_per_unit, 3)

    # Capital required with leverage warning
    position_value = position_size * entry_price
    capital_required = (position_value / leverage) if leverage > 0 else 0.0

    # Reward calculations
    reward_per_unit = abs(target_price - entry_price)
    expected_reward = reward_per_unit * position_size
    reward_to_risk = (expected_reward / risk_amount) if risk_amount > 0 else 0.0

    return (
        risk_amount,
        position_size,
        effective_stop_loss,
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
    effective_stop_loss: float,
    capital_required: float,
    expected_reward: float,
    reward_to_risk: float,
    liquid_capital: float,
    leverage: float,
    direction: str,
    entry_price: float,
):
    """Enhanced results display with additional warnings."""
    # Formatting functions
    def format_currency(val: float) -> str:
        return f"${val:,.3f}" if (val % 1) != 0 else f"${int(val):,}"

    def format_units(val: float) -> str:
        return f"{val:,.3f} units" if (val % 1) != 0 else f"{int(val):,} units"

    # Trade Summary
    st.markdown("---")
    st.subheader("📈 Trade Summary")

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.metric("💰 Max Risk Allowed", format_currency(risk_amount))
        st.metric("📦 Position Size", format_units(position_size))
        st.metric("🛑 Effective Stop Loss", format_currency(effective_stop_loss))
    with col2:
        st.metric("💸 Capital Required", format_currency(capital_required))
        st.metric("🎯 Expected Reward", format_currency(expected_reward))
        st.metric("⚖️ Reward-to-Risk", f"{reward_to_risk:.2f}:1")

    # Warnings Expander
    with st.expander("⚠️ Risk Notices", expanded=True):
        # Leverage warning
        if leverage >= MAX_LEVERAGE_WARNING:
            st.warning(
                f"⚡ High leverage detected (**{leverage}x**). "
                "This significantly increases risk of liquidation."
            )

        # Reward-to-risk warning
        if reward_to_risk < MIN_REWARD_RISK_RATIO:
            st.warning(
                f"⚠️ Reward-to-risk ratio (**{reward_to_risk:.2f}:1**) is below "
                f"recommended minimum (**{MIN_REWARD_RISK_RATIO}:1**)."
            )

        # Capital usage warnings
        if capital_required > liquid_capital:
            st.error(
                f"🚫 Required capital (**{format_currency(capital_required)}**) "
                f"exceeds your liquid capital (**{format_currency(liquid_capital)}**)."
            )
        elif capital_required > 0.8 * liquid_capital:
            st.warning(
                f"⚠️ Using **{capital_required/liquid_capital:.0%}** of your liquid capital. "
                "Consider smaller positions for better risk management."
            )

        # Volatility warning for tight stops
        risk_percentage = abs(entry_price - effective_stop_loss) / entry_price * 100
        if risk_percentage > 10:
            st.warning(
                f"🔔 Wide stop detected (**{risk_percentage:.1f}%** from entry). "
                "Ensure this matches the asset's volatility."
            )

    # Advanced Risk Management
    with st.expander("🧠 Advanced Risk Management", expanded=False):
        st.markdown("""
        **Portfolio-Level Considerations:**
        - 🔗 **Correlation Risk:** Multiple positions in similar assets (e.g., tech stocks) can compound losses
        - 📉 **Drawdown Control:** Never risk more than 5% of total capital across all open trades
        - 💧 **Liquidity Risk:** Large positions in low-volume assets may cause slippage

        **Volatility Tools:**
        - Use [ATR](https://www.tradingview.com/support/solutions/43000502348/) for dynamic stop-loss placement
        - Monitor [VIX](https://www.tradingview.com/symbols/VIX/) for market volatility
        """)

# ────────────────────────────────────────────────────────────────────────────────
# 🚀 Main Application
# ────────────────────────────────────────────────────────────────────────────────
def main():
    setup_page()
    display_header()

    # Get user inputs
    (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
        slippage_pct,
        use_atr,
        atr_value,
        atr_multiplier
    ) = get_user_inputs()

    # Calculate suggested stop loss
    current_suggested_stop = 0.0
    if use_atr and atr_value > 0:
        atr_distance = atr_value * atr_multiplier
        current_suggested_stop = (
            entry_price - atr_distance if direction == "Long" 
            else entry_price + atr_distance
        )
        current_suggested_stop = max(0.001, current_suggested_stop)
    else:
        risk_amount = liquid_capital * (risk_percent / 100)
        max_units = (liquid_capital * leverage) / entry_price if entry_price > 0 else 0
        risk_per_unit = (risk_amount / max_units) if max_units > 0 else 0
        current_suggested_stop = (
            entry_price - risk_per_unit if direction == "Long"
            else entry_price + risk_per_unit
        )
        current_suggested_stop = max(0.001, current_suggested_stop)

    # Stop Loss Input
    st.markdown("<h4>🛑 Stop Loss Adjustment</h4>", unsafe_allow_html=True)
    stop_loss_price = st.number_input(
        "Stop Loss Price ($)",
        min_value=0.000,
        value=round(current_suggested_stop, 3),
        step=0.001,
        format="%g",
        key="stop_loss_price",
    )

    # Calculate metrics
    try:
        (
            risk_amount,
            position_size,
            effective_stop_loss,
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
            slippage_pct,
        )
    except Exception as e:
        st.error(f"Calculation error: {str(e)}")
        st.stop()

    # Display results
    display_results(
        risk_amount,
        position_size,
        effective_stop_loss,
        capital_required,
        expected_reward,
        reward_to_risk,
        liquid_capital,
        leverage,
        direction,
        entry_price,
    )

    # Disclaimer
    st.markdown("---")
    st.subheader("📢 Disclaimer")
    if not st.checkbox("✅ I understand this is for educational purposes only"):
        st.warning("Please acknowledge the disclaimer to use the calculator")
        st.stop()

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #7F8C8D; font-size: 0.8em;'>"
        "© 2025 Quantum Ledger. Not financial advice."
        "</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
