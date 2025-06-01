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
            st.title("📊 1% Risk Management Calculator (Quantum Ledger)") # Updated title
    except FileNotFoundError:
        st.title("📊 1% Risk Management Calculator (Quantum Ledger)") # Updated title

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
    float,  # slippage_pct
    bool,   # use_atr
    float,  # atr_value (if used)
    float   # atr_multiplier (if used)
]:
    """
    Gather user inputs and return them. Grouped under subheaders styled by CSS.
    """
    col1, col2 = st.columns(2, gap="medium")

    # Panel for Capital Settings
    with col1:
        st.markdown("<h4>🏦 Capital Settings</h4>", unsafe_allow_html=True)
        # Wrap inputs in a div to apply panel styling below h4
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
        )
        st.markdown("</div>", unsafe_allow_html=True) # Close the panel div

    # Panel for Trade Settings
    with col2:
        st.markdown("<h4>📊 Trade Settings</h4>", unsafe_allow_html=True)
        # Wrap inputs in a div to apply panel styling below h4
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

        # NEW: Slippage Adjustment
        slippage_pct = st.number_input(
            "📉 Estimated Slippage (%)",
            min_value=0.000,
            value=0.050, # Default to 0.05%
            step=0.001,
            format="%g",
            key="slippage_pct",
            help="Factor in potential slippage (e.g., stop-loss fills at a worse price than intended)."
        ) / 100 # Convert to decimal

        st.markdown("</div>", unsafe_allow_html=True) # Close the panel div

    # NEW: ATR Settings (in its own section as it affects stop loss calculation)
    st.markdown("<h4 style='margin-top: 2rem;'>📊 Volatility-Based Stops (ATR)</h4>", unsafe_allow_html=True)
    st.markdown("<div>", unsafe_allow_html=True) # New panel for ATR
    use_atr = st.checkbox(
        "🔍 Use ATR-Based Stop Loss (Recommended for Volatile Assets)",
        value=False,
        key="use_atr",
        help="Use Average True Range (ATR) to set a dynamic stop loss."
    )

    atr_value = 0.0
    atr_multiplier = 0.0

    if use_atr:
        st.info(
            "**Note:** ATR is a measure of an asset's volatility. You need to look up "
            "the current ATR for your specific asset on a charting platform (e.g., "
            "TradingView) and enter it here. A common period is 14 bars (days/hours)."
        )
        atr_value = st.number_input(
            "📈 Average True Range (ATR) Value",
            min_value=0.000,
            value=0.000,
            step=0.001,
            format="%g",
            key="atr_value",
            help="Enter the ATR value for your asset (e.g., 2.50 for a stock)."
        )
        atr_multiplier = st.number_input(
            "✖️ ATR Multiplier",
            min_value=0.1,
            value=1.5,
            step=0.1,
            format="%g",
            key="atr_multiplier",
            help="Typical values are 1.5 to 3.0. Higher multiplier = wider stop."
        )
    st.markdown("</div>", unsafe_allow_html=True) # Close the ATR panel

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
    stop_loss_price: float, # User-entered or ATR-derived stop loss
    slippage_pct: float,    # NEW: Slippage percentage
) -> Tuple[
    float,  # risk_amount
    float,  # position_size
    float,  # effective_stop_loss (newly added for clarity)
    float,  # capital_required
    float,  # expected_reward
    float,  # reward_to_risk
]:
    """
    Calculates trade metrics including slippage.
    """
    # 1) Dollar amount you’re risking
    risk_amount = liquid_capital * (risk_percent / 100)

    # 2) Calculate effective stop loss price due to slippage
    effective_stop_loss = stop_loss_price
    if slippage_pct > 0:
        if direction == "Long":
            # For long, slippage makes stop lower (worse)
            effective_stop_loss = stop_loss_price * (1 - slippage_pct)
        else: # "Short"
            # For short, slippage makes stop higher (worse)
            effective_stop_loss = stop_loss_price * (1 + slippage_pct)

    # Validate effective stop loss relative to entry price
    if direction == "Long" and effective_stop_loss >= entry_price:
        st.error("🚫 For a Long trade, the **effective** Stop Loss Price must be below Entry Price.")
        st.stop()
    if direction == "Short" and effective_stop_loss <= entry_price:
        st.error("🚫 For a Short trade, the **effective** Stop Loss Price must be above Entry Price.")
        st.stop()

    # 5) Actual risk per unit, based on effective_stop_loss
    actual_risk_per_unit = abs(entry_price - effective_stop_loss)

    if actual_risk_per_unit == 0:
        st.error("🚫 Cannot calculate position size: Effective Stop Loss Price is too close to Entry Price. Adjust Entry, Stop Loss, or Slippage.")
        st.stop()

    # 6) Final position size that risks exactly risk_amount
    position_size = (risk_amount / actual_risk_per_unit)

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
        effective_stop_loss, # Return the effective stop for display
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
    effective_stop_loss: float, # Now displaying effective stop
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
        st.metric(label="🛑 Effective Stop Loss", value=format_currency(effective_stop_loss)) # Display effective stop
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

    # NEW: Portfolio Risk Expander
    with st.expander("🧠 Advanced Risk Management: Portfolio & Volatility Considerations"):
        st.markdown(
            """
            This calculator focuses on single-trade risk, but truly robust risk management extends to your entire portfolio.
            **Consider these points:**

            **1. Portfolio-Level Risk & Correlation:**
            Even if each trade risks 1%, having multiple open trades that are **highly correlated** (e.g., several tech stocks, different cryptocurrencies during a market-wide event) can lead to a much larger overall loss if the sector or market crashes.
            -   **Recommendation:** Limit your total capital at risk across *all* open positions (e.g., to a maximum of 5% of your total capital). Track your open positions and their collective exposure. Avoid overconcentration in any single sector or asset class.

            **2. Liquidity Risk:**
            Trading in markets with low liquidity (low trading volume) can lead to **significant slippage**, especially with larger position sizes. Your stop-loss might not fill at the price you expect, increasing your actual loss.
            -   **Recommendation:** Be aware of the average daily volume of the asset you're trading. If your calculated position value is a substantial percentage (e.g., >1% or >5%) of the asset's average daily volume, consider if you can exit without moving the market significantly.

            **3. Dynamic Position Sizing (ATR):**
            Using ATR (Average True Range) helps set stop losses that are adaptive to an asset's actual volatility, reducing the chance of being stopped out by normal market "noise" and allowing for more appropriate position sizing based on risk. More volatile assets should lead to smaller position sizes if your dollar risk is fixed.

            Remember: This calculator is a powerful tool, but it's part of a larger risk management strategy. Always combine it with comprehensive portfolio tracking and continuous learning about market dynamics.
            """
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
        "© 2025 Quantum Ledger. All rights reserved." # Updated footer text
        "</p>",
        unsafe_allow_html=True
    )


# ────────────────────────────────────────────────────────────────────────────────
# 🚀 Main Application
# ────────────────────────────────────────────────────────────────────────────────
def main():
    setup_page()
    display_header()

    # 1️⃣ Gather inputs (including new slippage and ATR settings)
    (
        total_capital,
        liquid_capital,
        risk_percent,
        entry_price,
        direction,
        target_price,
        leverage,
        slippage_pct,      # NEW
        use_atr,           # NEW
        atr_value,         # NEW
        atr_multiplier     # NEW
    ) = get_user_inputs()

    # 2️⃣ Precompute suggested_stop to pre-fill the Stop Loss widget
    current_suggested_stop = 0.0

    if use_atr and atr_value > 0 and atr_multiplier > 0:
        # NEW: ATR-based suggested stop
        atr_distance = atr_value * atr_multiplier
        if direction == "Long":
            current_suggested_stop = entry_price - atr_distance
        else:  # "Short"
            current_suggested_stop = entry_price + atr_distance
        # Ensure it doesn't go below zero for long, or too high for short if entry is low
        current_suggested_stop = max(0.001, current_suggested_stop) if direction == "Long" else current_suggested_stop
    else:
        # Original risk-based suggested stop if ATR is not used or invalid
        risk_amount_for_suggested_stop = liquid_capital * (risk_percent / 100)
        max_position_value_for_suggested_stop = liquid_capital * leverage
        max_units_for_suggested_stop = (max_position_value_for_suggested_stop / entry_price) if entry_price > 0 else 0.0
        required_risk_per_unit_for_suggested_stop = (risk_amount_for_suggested_stop / max_units_for_suggested_stop) if max_units_for_suggested_stop > 0 else 0.0

        if direction == "Long":
            current_suggested_stop = entry_price - required_risk_per_unit_for_suggested_stop
        else:
            current_suggested_stop = entry_price + required_risk_per_unit_for_suggested_stop
        # Ensure it doesn't go below zero for long
        current_suggested_stop = max(0.001, current_suggested_stop) if direction == "Long" else current_suggested_stop

    # Round the suggested stop for display
    current_suggested_stop = round(current_suggested_stop, 3)


    # 3️⃣ Show the Stop Loss widget (pre-filled with suggested_stop, with 🛑 icon)
    # The stop loss input needs to be outside the input panels as it's computed
    # after the initial inputs.
    st.markdown("<h4 style='margin-top: 2rem;'>🛑 Stop Loss Adjustment</h4>", unsafe_allow_html=True)
    st.markdown("<div>", unsafe_allow_html=True) # New panel for Stop Loss
    stop_loss_price = st.number_input(
        "🛑 Stop Loss Price ($)",
        min_value=0.000,
        value=current_suggested_stop, # Use the calculated suggested stop
        step=0.001,
        format="%g",
        key="stop_loss_price",
        help="Pre-filled with suggested stop-loss (ATR-based if enabled); override as needed.",
    )
    st.markdown("</div>", unsafe_allow_html=True) # Close the stop loss panel

    # 4️⃣ Perform full trade calculations
    (
        risk_amount,
        position_size,
        effective_stop_loss, # Now includes slippage
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
        slippage_pct, # Pass slippage to calculation
    )

    # 5️⃣ Show results + warnings
    display_results(
        risk_amount,
        position_size,
        effective_stop_loss, # Pass the effective stop loss
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
