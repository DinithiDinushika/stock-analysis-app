"""
Reusable UI components, KPI metric banners, and compliance notices for Streamlit.
"""

from typing import Dict, Any
import streamlit as st


def render_company_header(quote: Dict[str, Any], profile: Dict[str, Any]):
    """
    Renders the company branding, sector badges, live price, and daily change.
    """
    company_name = quote.get("company_name", quote.get("ticker", ""))
    ticker = quote.get("ticker", "")
    price = quote.get("current_price", 0.0)
    change = quote.get("change", 0.0)
    change_pct = quote.get("change_percent", 0.0)
    sector = profile.get("sector", "N/A")
    industry = profile.get("industry", "N/A")

    change_color = "#26a69a" if change >= 0 else "#ef5350"
    change_icon = "▲" if change >= 0 else "▼"
    change_str = f"{change_icon} ${abs(change):.2f} ({change_pct:+.2f}%) Today"

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 5px;">
                <h1 style="margin: 0; font-size: 2.2rem; display: inline;">{company_name}</h1>
                <span style="font-size: 1.3rem; color: #7f8c8d; font-weight: 600; margin-left: 8px;">({ticker})</span>
            </div>
            <div style="margin-bottom: 12px;">
                <span style="background-color: #f0f2f6; color: #2c3e50; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 500;">
                    📁 {sector}
                </span>
                <span style="background-color: #f0f2f6; color: #2c3e50; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 500; margin-left: 6px;">
                    🏭 {industry}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="text-align: right;">
                <div style="font-size: 2.2rem; font-weight: 700; color: #1e272e;">${price:.2f}</div>
                <div style="font-size: 1.05rem; font-weight: 600; color: {change_color};">
                    {change_str}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metric_banner(quote: Dict[str, Any], fundamentals: Dict[str, Any], technicals: Dict[str, Any]):
    """
    Renders clean KPI metric cards across two rows:
    Row 1: Valuation & Solvency
    Row 2: Momentum & Downside Risk
    """
    st.markdown("### 📊 Key Financial & Technical Metrics")

    # Row 1: Valuation & Solvency
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="Market Cap",
            value=fundamentals.get("market_cap", "N/A"),
            help="Total dollar market value of a company's outstanding shares."
        )
    with c2:
        pe = fundamentals.get("pe_ratio")
        pe_str = f"{pe:.1f}x" if pe else "N/A"
        st.metric(
            label="P/E Ratio",
            value=pe_str,
            help="Price-to-Earnings ratio. Valuation multiple relative to trailing/forward earnings."
        )
    with c3:
        eps = fundamentals.get("eps")
        eps_str = f"${eps:.2f}" if eps is not None else "N/A"
        st.metric(
            label="EPS (Diluted)",
            value=eps_str,
            help="Earnings Per Share. Net income divided by available shares."
        )
    with c4:
        pm = fundamentals.get("profit_margin_pct")
        pm_str = f"{pm:.1f}%" if pm is not None else "N/A"
        st.metric(
            label="Profit Margin",
            value=pm_str,
            help="Percentage of revenue remaining as profit after expenses."
        )

    # Row 2: Momentum & Downside Risk
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        hi_52 = quote.get("fifty_two_week_high")
        lo_52 = quote.get("fifty_two_week_low")
        rng_str = f"${lo_52:.1f} - ${hi_52:.1f}" if hi_52 and lo_52 else "N/A"
        st.metric(
            label="52-Week Range",
            value=rng_str,
            help="The lowest and highest price at which a stock has traded over the previous 52 weeks."
        )
    with c6:
        rsi = technicals.get("rsi_14")
        rsi_str = f"{rsi:.1f}" if rsi is not None else "N/A"
        rsi_status = technicals.get("rsi_signal", "")
        st.metric(
            label="RSI (14)",
            value=rsi_str,
            delta=rsi_status if rsi_status else None,
            delta_color="off",
            help="Relative Strength Index. <30 is oversold, >70 is overbought."
        )
    with c7:
        vol = technicals.get("annualized_volatility_30d_pct")
        vol_str = f"{vol:.1f}%" if vol is not None else "N/A"
        st.metric(
            label="30D Volatility",
            value=vol_str,
            help="Annualized 30-day standard deviation of daily stock returns."
        )
    with c8:
        dd = technicals.get("max_drawdown_pct")
        dd_str = f"{dd:.1f}%" if dd is not None else "N/A"
        st.metric(
            label="Max Drawdown",
            value=dd_str,
            help="Maximum observed peak-to-trough decline over the selected period."
        )


def render_verified_badge():
    """
    Renders the data verification trust badge.
    """
    st.info(
        "🟢 **Deterministic Data Layer**: All prices, moving averages, valuation ratios, and technical indicators "
        "are retrieved directly from live exchanges and calculated deterministically in Python before being interpreted by AI agents."
    )


# def render_disclaimer():
#     """
#     Renders the mandatory regulatory compliance disclaimer.
#     """
#     st.markdown("---")
#     st.markdown(
#         """
#         <div style="background-color: #f8f9fa; border-left: 4px solid #f39c12; padding: 12px 16px; border-radius: 4px; font-size: 0.85rem; color: #576574;">
#             <strong>⚠️ Regulatory & Compliance Notice:</strong><br>
#             This platform uses autonomous AI agents for informational, educational, and research purposes only. 
#             Nothing contained herein constitutes financial, investment, legal, or tax advice. Market investments involve substantial 
#             risk of capital loss. Always conduct independent due diligence or consult a licensed financial advisor before making investment decisions.
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

