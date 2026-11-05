"""
Specialized CrewAI Agent definitions for the Stock Market Intelligence Platform.
Implements the 5 core domain agents following the Worker-Critic-Synthesizer architecture:
- 3 Domain Workers (Technical, Fundamental, News)
- 1 Adversarial Critic (Risk & Fact Auditor)
- 1 Lead Synthesizer (Chief Investment Strategist)
"""

from typing import Tuple
from crewai import Agent, LLM
from src.tools.stock_tools import (
    get_stock_quote_tool,
    get_fundamental_metrics_tool,
    get_company_profile_tool,
)
from src.tools.indicator_tools import (
    get_technical_analysis_tool,
)
from src.tools.news_tools import (
    get_stock_news_tool,
)
from src.tools.market_tools import (
    get_market_movers_tool,
    get_sector_performance_tool,
)


def create_stock_agents(llm: LLM) -> Tuple[Agent, Agent, Agent, Agent, Agent]:
    """
    Creates and returns the 5 specialized domain agents.
    The same 5 agents power both Single Stock Analysis and Market Trend Scanner workflows.
    """

    # 1. Technical & Quantitative Analyst (Worker: Momentum & Price Action)
    technical_analyst = Agent(
        role="Senior Technical Market Analyst",
        goal="Evaluate price momentum, 50-day and 200-day SMAs, RSI levels, MACD crossovers, historical volatility, and maximum drawdown.",
        backstory=(
            "Chartered Market Technician (CMT) who translates quantitative chart indicators "
            "into clear trend, momentum, and volatility assessments."
        ),
        tools=[
            get_technical_analysis_tool,
            get_stock_quote_tool,
            get_sector_performance_tool,
        ],
        llm=llm,
        verbose=True,
        memory=False,
    )

    # 2. Fundamental & Valuation Analyst (Worker: Financial Statements & Health)
    fundamental_analyst = Agent(
        role="Lead Equity Research Analyst",
        goal="Assess valuation multiples (P/E, Market Cap), earnings quality (EPS), margins, and balance sheet solvency (Debt-to-Equity).",
        backstory=(
            "CFA charterholder focused on fundamental corporate health, valuation discipline, "
            "and separating high-quality businesses from speculative traps."
        ),
        tools=[
            get_fundamental_metrics_tool,
            get_company_profile_tool,
        ],
        llm=llm,
        verbose=True,
        memory=False,
    )

    # 3. Sentiment & News Intelligence Analyst (Worker: Catalysts & Qualitative)
    sentiment_analyst = Agent(
        role="Financial News & Sentiment Intelligence Specialist",
        goal="Identify breaking corporate news catalysts, management updates, and compute overall market sentiment polarity.",
        backstory=(
            "Financial news analyst skilled at cutting through media hype to identify the real "
            "corporate catalysts and sentiment driving stock price action."
        ),
        tools=[
            get_stock_news_tool,
            get_market_movers_tool,
        ],
        llm=llm,
        verbose=True,
        memory=False,
    )

    # 4. Risk & Fact-Check Auditor (Critic / Reflection Agent)
    # Does not call data tools; inspects and audits the specialists' outputs to eliminate hallucinations and build the Bear Case.
    risk_auditor = Agent(
        role="Chief Risk & Compliance Auditor",
        goal="Formulate the Bear Case, stress-test downside risks, and audit numerical claims against verified tool outputs.",
        backstory=(
            "Independent risk officer with a zero-tolerance policy for AI hallucinations. "
            "Acts as the objective adversary: stress-tests the bull thesis and ensures data accuracy."
        ),
        tools=[],  # Pure cognitive critic; evaluates the previous specialists' findings
        llm=llm,
        verbose=True,
        memory=False,
    )

    # 5. Master Strategist & Portfolio Manager (Synthesizer & Lead Orchestrator)
    strategist = Agent(
        role="Chief Investment Strategist",
        goal="Synthesize specialist analyses into a cohesive, executive-ready investment dossier with an actionable outlook and clear confidence level.",
        backstory=(
            "Senior institutional portfolio manager who balances technical, fundamental, news, "
            "and risk evidence into an authoritative, publication-ready investment brief."
        ),
        tools=[],  # Pure synthesizer; merges all verified reports into the final dossier
        llm=llm,
        verbose=True,
        memory=False,
    )

    return strategist, technical_analyst, fundamental_analyst, sentiment_analyst, risk_auditor
