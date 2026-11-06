"""
CrewAI Task definitions for the Stock Market Intelligence Platform.
Streamlined, non-redundant task pipelines for both Single Stock Deep-Dive
and Market Trend Scanner workflows.
"""

from typing import List, Tuple
from crewai import Agent, Task


def create_stock_analysis_tasks(
    ticker: str,
    start_date: str,
    end_date: str,
    agents: Tuple[Agent, Agent, Agent, Agent, Agent]
) -> List[Task]:
    """
    Sequential pipeline for single stock deep-dive:
    Technical -> Fundamental -> News/Sentiment -> Risk Audit -> Final Dossier.
    """
    strategist, technical_analyst, fundamental_analyst, sentiment_analyst, risk_auditor = agents
    ticker_clean = ticker.strip().upper()

    # 1. Technical Task (Worker)
    technical_task = Task(
        description=(
            f"Analyze price action and quantitative momentum for '{ticker_clean}' over the date range from '{start_date}' to '{end_date}'.\n"
            f"- Fetch technical indicators via 'Get Technical Analysis and Indicators Tool' with start_date='{start_date}' and end_date='{end_date}' (RSI, MACD, 50 SMA, 200 SMA, 30-Day Volatility %, Max Drawdown %).\n"
            f"- Fetch current quote via 'Get Stock Quote Tool' (Price, Day Change %, 52-Week Range).\n"
            f"- Evaluate trend direction (Golden/Death Cross, Price vs 50/200 SMA), momentum (RSI overbought/oversold, MACD signal cross), and historical risk across the selected date range."
        ),
        expected_output=(
            f"A structured technical summary for {ticker_clean} from {start_date} to {end_date} containing:\n"
            f"- Exact values: Price, 50 SMA, 200 SMA, RSI (14), MACD, 30-Day Volatility %, Max Drawdown %\n"
            f"- Trend status (Bullish / Bearish / Neutral)\n"
            f"- Key support and resistance levels"
        ),
        agent=technical_analyst,
    )

    # 2. Fundamental Task (Worker)
    fundamental_task = Task(
        description=(
            f"Evaluate the corporate valuation, earnings power, and solvency of '{ticker_clean}'.\n"
            f"- Fetch financial ratios via 'Get Fundamental Financial Metrics Tool' (Market Cap, P/E Ratio, EPS, Profit Margin %, Debt-to-Equity).\n"
            f"- Fetch profile via 'Get Company Profile Tool' (Sector, Industry, Core Business Model).\n"
            f"- Assess whether valuation is attractive or stretched, verify profit margins, and evaluate balance sheet debt risk."
        ),
        expected_output=(
            f"A structured fundamental evaluation for {ticker_clean} containing:\n"
            f"- Profile: Sector, Industry, Business Overview\n"
            f"- Valuation: Market Cap, P/E Ratio, EPS\n"
            f"- Financial Health: Profit Margin %, Debt-to-Equity, Solvency Assessment"
        ),
        agent=fundamental_analyst,
    )

    # 3. News & Sentiment Task (Worker)
    sentiment_task = Task(
        description=(
            f"Investigate recent news headlines and qualitative sentiment for '{ticker_clean}'.\n"
            f"- Fetch recent news via 'Get Stock News and Sentiment Tool'.\n"
            f"- Identify 2-3 prominent news catalysts (earnings reports, guidance, product launches, regulatory updates).\n"
            f"- Report the net sentiment polarity (Bullish, Bearish, or Neutral) and cite top headlines with dates."
        ),
        expected_output=(
            f"A news intelligence briefing for {ticker_clean} containing:\n"
            f"- Net Sentiment: Bullish, Bearish, or Neutral\n"
            f"- Top 2-3 catalysts driving the stock\n"
            f"- Bulleted list of recent verified headlines"
        ),
        agent=sentiment_analyst,
    )

    # 4. Risk Audit & Fact-Check Task (Critic)
    risk_task = Task(
        description=(
            f"Conduct an independent adversarial risk audit for '{ticker_clean}'.\n"
            f"- Review findings from the Technical, Fundamental, and Sentiment specialists.\n"
            f"- Fact-Check: Verify all numbers quoted (Price, P/E, RSI, Max Drawdown) match reported facts.\n"
            f"- Formulate the Bear Case: Identify top 3 downside risks (elevated valuation, debt burden, drawdown vulnerability, negative news).\n"
            f"- Assign an overall Risk Level: Low, Moderate, High, or Speculative."
        ),
        expected_output=(
            f"An independent risk audit for {ticker_clean} containing:\n"
            f"- Fact-check confirmation of numbers\n"
            f"- The Bear Case (3-4 explicit downside risk factors)\n"
            f"- Overall Risk Classification (Low / Moderate / High / Speculative)"
        ),
        agent=risk_auditor,
    )

    # 5. Executive Dossier Synthesis Task (Synthesizer)
    synthesis_task = Task(
        description=(
            f"Compile the final Investment Intelligence Dossier for '{ticker_clean}'.\n"
            f"- Combine Technical, Fundamental, News, and Risk findings into an executive-ready brief.\n"
            f"- Clearly distinguish VERIFIED FACTUAL DATA from AI INTERPRETATION.\n"
            f"- Deliver an Executive Summary with an Outlook (Bullish / Neutral / Bearish) and Confidence score (1-10).\n"
            f"- Provide a clean Markdown Fact Sheet table with Price, Market Cap, P/E, EPS, RSI, SMAs, Volatility %, and Max Drawdown %.\n"
            f"- Include balanced Bull Case and Bear Case sections.\n"
            f"- Conclude with the mandatory regulatory informational disclaimer."
        ),
        expected_output=(
            f"A polished Markdown investment brief for {ticker_clean} containing:\n"
            f"# Investment Intelligence Report: {ticker_clean}\n"
            f"## 1. Executive Summary & Outlook (Verdict & Confidence Score)\n"
            f"## 2. Verified Financial Fact Sheet (Markdown Table)\n"
            f"## 3. Technical & Momentum Analysis\n"
            f"## 4. Fundamental Health & Valuation\n"
            f"## 5. News Catalysts & Sentiment\n"
            f"## 6. Risk Matrix & Bear Case\n"
            f"## 7. Regulatory Disclaimer"
        ),
        agent=strategist,
    )

    return [technical_task, fundamental_task, sentiment_task, risk_task, synthesis_task]


def create_market_scanner_tasks(
    agents: Tuple[Agent, Agent, Agent, Agent, Agent]
) -> List[Task]:
    """
    Sequential pipeline for the Market Trend Scanner using the same 5 domain agents:
    Discovery & News -> Sector Breadth -> Quality Check -> Risk Warning -> Market Briefing.
    """
    strategist, technical_analyst, fundamental_analyst, sentiment_analyst, risk_auditor = agents

    # 1. Discovery & News Catalyst Task (Sentiment Specialist)
    discovery_task = Task(
        description=(
            "Identify today's leading market movers and explain WHY they are moving.\n"
            "- Use 'Get Market Movers Tool' to retrieve Top 5 Gainers, Top 5 Losers, and Top 5 Most Active stocks.\n"
            "- For the top gainers and losers, use 'Get Stock News and Sentiment Tool' to discover the exact news reasons "
            "(earnings beat, FDA decision, analyst upgrade/downgrade, M&A) behind their moves."
        ),
        expected_output=(
            "A Market Movers Briefing containing:\n"
            "- Tables of Top Gainers, Losers, and Most Active equities\n"
            "- Verified news catalysts explaining why each prominent mover surged or plummeted"
        ),
        agent=sentiment_analyst,
    )

    # 2. Sector Performance & Technical Breadth Task (Technical Specialist)
    breadth_task = Task(
        description=(
            "Evaluate broad market breadth and sector rotation.\n"
            "- Use 'Get Sector Performance Tool' to analyze performance across the 11 SPDR Sector ETFs.\n"
            "- Identify leading vs. lagging sectors and determine whether the market is Risk-On or Risk-Off."
        ),
        expected_output=(
            "A Technical Breadth and Sector Rotation Report containing:\n"
            "- Sector performance rankings\n"
            "- Leading and lagging sectors breakdown\n"
            "- Macro breadth assessment (Risk-On vs. Defensive)"
        ),
        agent=technical_analyst,
    )

    # 3. Fundamental Quality Screening Task (Fundamental Specialist)
    quality_task = Task(
        description=(
            "Screen the identified top market gainers for fundamental business quality.\n"
            "- Use 'Get Fundamental Financial Metrics Tool' on the key movers.\n"
            "- Separate fundamentally supported moves (profitable, real earnings, healthy margins) from speculative, low-quality penny-stock rallies."
        ),
        expected_output=(
            "A Quality Screen of market movers classifying rallies as:\n"
            "- 'Fundamentally Supported' (Real earnings & profitable growth)\n"
            "- 'Speculative / High-Risk' (Unprofitable, momentum-driven)"
        ),
        agent=fundamental_analyst,
    )

    # 4. Market Risk & Volatility Alert Task (Risk Auditor)
    market_risk_task = Task(
        description=(
            "Assess systemic risk factors based on today's market action.\n"
            "- Warn against chasing low-float volatility traps, sudden dilution risk in hyper-gaining penny stocks, and sector contagion.\n"
            "- Formulate capital preservation advice for volatile market conditions."
        ),
        expected_output=(
            "A Market Risk Alert containing:\n"
            "- Immediate risks (speculative traps, extreme volatility)\n"
            "- Actionable capital preservation rules"
        ),
        agent=risk_auditor,
    )

    # 5. Master Market Intelligence Briefing Task (Synthesizer)
    master_briefing_task = Task(
        description=(
            "Synthesize the specialist reports into an executive Daily Market Trend Briefing.\n"
            "- Summarize market pulse, sector rotation, and the top movers with verified news explanations.\n"
            "- Highlight fundamental quality check findings and risk warnings.\n"
            "- Provide a clear, strategic investor takeaway and compliance disclaimer."
        ),
        expected_output=(
            "A publication-ready Markdown Market Intelligence Briefing containing:\n"
            "# Daily Stock Market Intelligence & Trend Briefing\n"
            "## 1. Market Pulse & Executive Summary\n"
            "## 2. Sector Performance & Macro Breadth (Leaders vs. Laggards)\n"
            "## 3. Top Market Movers & Verified News Drivers\n"
            "## 4. Fundamental Quality Check: Real Earnings vs. Speculative Hype\n"
            "## 5. Market Risk Warnings & Capital Preservation\n"
            "## 6. Strategic Takeaway for Investors\n"
            "## 7. Regulatory Disclaimer"
        ),
        agent=strategist,
    )

    return [discovery_task, breadth_task, quality_task, market_risk_task, master_briefing_task]
