"""
MarketMind AI - Pure Agentic AI Stock Market Intelligence Platform
Demonstrating Multi-Agent Collaboration, Autonomous Tool Calling, and Adversarial Risk Auditing.
Powered by CrewAI, Streamlit, and Google Gemini.
"""

import datetime
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="MarketMind AI - Agentic Stock Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.config import GEMINI_API_KEY, GEMINI_MODEL, ALPHA_VANTAGE_API_KEY
from src.crew import (
    run_stock_analysis_crew,
    run_market_scanner_crew,
)
from src.ui.export_pdf import generate_dossier_pdf

# -------------------------------------------------------------
# SIDEBAR: AGENTIC AI ARCHITECTURE & CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🤖 MarketMind AI")
    st.caption("Autonomous Multi-Agent Financial Intelligence")
    st.markdown("---")

    # Workflow Selector
    workflow_mode = st.radio(
        "Select Agentic Workflow:",
        ["🎯 Single Stock Deep-Dive", "🌐 Market Trend Scanner"],
        index=0,
    )

    st.markdown("---")

    # LLM Connection Status
    if GEMINI_API_KEY:
        st.success(f"🟢 Gemini Active (`{GEMINI_MODEL}`)")
    else:
        st.error("🔴 GEMINI_API_KEY Missing")
        st.info("Add your Gemini key to `.env` to enable autonomous agent execution.")

    # Alpha Vantage Status
    if ALPHA_VANTAGE_API_KEY:
        st.success("🟢 Alpha Vantage Active")
    else:
        st.caption("⚪ Alpha Vantage: Optional (Open feed fallback)")


# -------------------------------------------------------------
# WORKFLOW 1: SINGLE STOCK DEEP-DIVE
# -------------------------------------------------------------
if workflow_mode == "🎯 Single Stock Deep-Dive":

    st.markdown("# Autonomous Single Stock Intelligence")

    # User Input Panel with From and To Date Pickers (Default 3-month window)
    today = datetime.date.today()
    default_from = today - datetime.timedelta(days=90)

    c_ticker, c_from, c_to, c_btn = st.columns([1.5, 1.2, 1.2, 1.6])

    with c_ticker:
        if "input_ticker" not in st.session_state:
            st.session_state["input_ticker"] = "NVDA"
        ticker_val = st.text_input(
            "Target Stock Ticker:",
            value=st.session_state["input_ticker"],
            max_chars=10,
        ).strip().upper()

    with c_from:
        start_date = st.date_input(
            "From Date:",
            value=default_from,
            max_value=today,
        )

    with c_to:
        end_date = st.date_input(
            "To Date:",
            value=today,
            max_value=today,
        )

    with c_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        launch_btn = st.button("🚀 Analyze Stock", type="primary", use_container_width=True)

    # Date validation
    date_valid = True
    if start_date >= end_date:
        st.error("⚠️ **Invalid Date Range:** 'From Date' must be before 'To Date'.")
        date_valid = False

    # Quick Select Buttons
    st.markdown("<small>Quick Presets:</small>", unsafe_allow_html=True)
    p_cols = st.columns(6)
    for i, sym in enumerate(["NVDA", "AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"]):
        with p_cols[i]:
            if st.button(sym, key=f"preset_{sym}", use_container_width=True):
                st.session_state["input_ticker"] = sym
                st.rerun()

    active_ticker = ticker_val if ticker_val else "NVDA"
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    cache_key = f"agent_result_{active_ticker}_{start_str}_{end_str}"

    # Agent Execution Trigger
    if launch_btn and date_valid:
        if not GEMINI_API_KEY:
            st.warning("⚠️ Please configure your `GEMINI_API_KEY` in the `.env` file to launch the AI agents.")
        else:
            with st.status(f"🤖 5-Agent Committee Analyzing {active_ticker} ({start_str} to {end_str})...", expanded=True) as status:
                st.write(f"📊 **Technical Analyst**: Invoking indicators tool for {start_str} to {end_str} (50/200 SMA, RSI, MACD, Max Drawdown)...")
                st.write("🏢 **Fundamental Analyst**: Invoking metrics tool to inspect P/E, EPS, Profit Margin, and Debt-to-Equity...")
                st.write("📰 **News Analyst**: Invoking news tool to scan recent headlines and assess sentiment polarity...")
                st.write("🛡️ **Risk Auditor**: Conducting adversarial review, fact-checking numbers, and formulating the Bear Case...")
                st.write("📑 **Chief Strategist**: Synthesizing evidence into the final structured Investment Dossier...")

                result = run_stock_analysis_crew(active_ticker, start_date=start_str, end_date=end_str)

                if result.get("success"):
                    st.session_state[cache_key] = result
                    status.update(label=f"✅ Multi-Agent Analysis for {active_ticker} Complete!", state="complete", expanded=False)
                else:
                    status.update(label="❌ Analysis Execution Failed", state="error", expanded=True)
                    st.error(result.get("error", "An error occurred during agent execution."))

    # Display Agent Results (Only rendered when agent workflow has executed)
    if cache_key in st.session_state and st.session_state[cache_key].get("success"):
        res = st.session_state[cache_key]
        full_dossier = res.get("report", "")
        agent_outputs = res.get("agent_outputs", {})

        st.markdown("---")

        # Display tabs for each agent in the committee
        tab_dossier, tab_tech, tab_fund, tab_news, tab_risk = st.tabs([
            "📑 Final Dossier (Chief Strategist)",
            "📊 Technical Analyst Output",
            "🏢 Fundamental Analyst Output",
            "📰 News Analyst Output",
            "🛡️ Risk Auditor Output",
        ])

        # Tab 1: Executive Dossier from Strategist
        with tab_dossier:
            st.markdown(full_dossier)
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label="📥 Download Dossier (.md)",
                    data=full_dossier,
                    file_name=f"{active_ticker}_Agentic_Investment_Dossier.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with d_col2:
                try:
                    pdf_bytes = generate_dossier_pdf(full_dossier, active_ticker)
                    st.download_button(
                        label="📄 Download Dossier (.pdf)",
                        data=pdf_bytes,
                        file_name=f"{active_ticker}_Agentic_Investment_Dossier.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception:
                    pass

        # Tab 2: Technical Specialist Output
        with tab_tech:
            st.markdown("### 📊 Senior Technical Analyst Report")
            tech_text = agent_outputs.get(
                "Senior Technical Market Analyst",
                "Technical findings integrated into the Executive Dossier."
            )
            st.markdown(tech_text)

        # Tab 3: Fundamental Specialist Output
        with tab_fund:
            st.markdown("### 🏢 Lead Equity Research Analyst Report")
            fund_text = agent_outputs.get(
                "Lead Equity Research Analyst",
                "Fundamental findings integrated into the Executive Dossier."
            )
            st.markdown(fund_text)

        # Tab 4: News & Sentiment Specialist Output
        with tab_news:
            st.markdown("### 📰 Financial News & Sentiment Intelligence Report")
            news_text = agent_outputs.get(
                "Financial News & Sentiment Intelligence Specialist",
                "News and catalyst findings integrated into the Executive Dossier."
            )
            st.markdown(news_text)

        # Tab 5: Risk & Compliance Auditor Output
        with tab_risk:
            st.markdown("### 🛡️ Chief Risk & Compliance Auditor Report")
            risk_text = agent_outputs.get(
                "Chief Risk & Compliance Auditor",
                "Risk audit and fact-checking findings integrated into the Executive Dossier."
            )
            st.markdown(risk_text)

    else:
        st.info("👆 Enter a ticker symbol above and click **'🚀 Launch Multi-Agent Workflow'** to start the autonomous committee.")


# -------------------------------------------------------------
# WORKFLOW 2: MARKET TREND SCANNER
# -------------------------------------------------------------
else:
    st.markdown("# Autonomous Market Trend & Movers Scanner")

    st.markdown("---")
    scan_col1, scan_col2 = st.columns([1, 3])

    with scan_col1:
        launch_scan_btn = st.button("🚀 Launch Multi-Agent Market Scan", type="primary", use_container_width=True)

    scan_cache_key = "agent_market_scan_result"

    if launch_scan_btn:
        if not GEMINI_API_KEY:
            st.warning("⚠️ Please configure your `GEMINI_API_KEY` in the `.env` file to launch the market scanner.")
        else:
            with st.status("🤖 5-Agent Committee Scanning Market Trends...", expanded=True) as status:
                st.write("📰 **News Analyst**: Discovering top gainers/losers & scanning breaking news to explain price action...")
                st.write("📊 **Technical Analyst**: Analyzing S&P 500 sector rotation & macro breadth across 11 SPDR ETFs...")
                st.write("🏢 **Fundamental Analyst**: Screening movers to differentiate real earnings from speculative hype...")
                st.write("🛡️ **Risk Auditor**: Identifying low-float volatility traps and sector contagion risks...")
                st.write("📑 **Chief Strategist**: Authoring the Daily Market Intelligence Briefing...")

                scan_res = run_market_scanner_crew()

                if scan_res.get("success"):
                    st.session_state[scan_cache_key] = scan_res
                    status.update(label="✅ Market Trend Scan Complete!", state="complete", expanded=False)
                else:
                    status.update(label="❌ Market Scan Failed", state="error", expanded=True)
                    st.error(scan_res.get("error", "Error occurred during market scan execution."))

    # Display Scan Results (Only after agent execution)
    if scan_cache_key in st.session_state and st.session_state[scan_cache_key].get("success"):
        res = st.session_state[scan_cache_key]
        report_text = res.get("report", "")

        st.markdown("---")

        # Display the Agent's Master Report
        st.markdown(report_text)

        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.download_button(
                label="📥 Download Briefing (.md)",
                data=report_text,
                file_name="Daily_Market_Intelligence_Briefing.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with m_col2:
            try:
                scan_pdf = generate_dossier_pdf(report_text, "MARKET_SCAN")
                st.download_button(
                    label="📄 Download Briefing (.pdf)",
                    data=scan_pdf,
                    file_name="Daily_Market_Intelligence_Briefing.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception:
                pass

    else:
        st.info("👆 Click **'🚀 Launch Multi-Agent Market Scan'** above to trigger the 5-agent team across the market.")
