"""
Crew orchestration engine for the Stock Market Intelligence Platform.
Manages Crew instantiation and execution for both Single Stock Deep-Dive
and Market Trend Scanner workflows.
"""

from typing import Dict, Any
from crewai import Crew, Process
from src.config import get_llm
from src.agents.stock_agents import create_stock_agents
from src.agents.tasks import (
    create_stock_analysis_tasks,
    create_market_scanner_tasks,
)
from src.tools.indicator_tools import (
    get_historical_ohlcv,
    calculate_technical_indicators,
)
from src.tools.stock_tools import get_stock_quote
from src.tools.market_tools import (
    get_market_movers,
    get_sector_performance,
)


def run_stock_analysis_crew(
    ticker: str,
    start_date: str = None,
    end_date: str = None,
    period: str = "1y"
) -> Dict[str, Any]:
    """
    Executes the 5-agent sequential workflow for a single stock ticker across a date range.
    Returns the final synthesized dossier, individual specialist agent findings,
    and supporting chart data.
    """
    ticker_clean = ticker.strip().upper()
    try:
        llm = get_llm()
        agents = create_stock_agents(llm)
        tasks = create_stock_analysis_tasks(ticker_clean, start_date or "1y ago", end_date or "today", agents)

        crew = Crew(
            agents=list(agents),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()

        # Extract individual task outputs for each agent
        task_outputs = {}
        if hasattr(crew, "tasks"):
            for t in crew.tasks:
                agent_role = getattr(t.agent, "role", "Specialist")
                output_str = str(t.output.raw) if hasattr(t, "output") and hasattr(t.output, "raw") else str(t.output)
                task_outputs[agent_role] = output_str

        # Retrieve chart data associated with this agent analysis
        chart_df = get_historical_ohlcv(ticker_clean, start_date=start_date, end_date=end_date, period=period)
        if not chart_df.empty:
            chart_df, _ = calculate_technical_indicators(chart_df)
        quote_data = get_stock_quote(ticker_clean)

        return {
            "success": True,
            "ticker": ticker_clean,
            "start_date": start_date,
            "end_date": end_date,
            "report": str(result.raw) if hasattr(result, "raw") else str(result),
            "agent_outputs": task_outputs,
            "chart_df": chart_df,
            "quote_data": quote_data,
        }

    except Exception as e:
        return {
            "success": False,
            "ticker": ticker_clean,
            "error": f"Failed to complete stock analysis for {ticker_clean}: {str(e)}"
        }


def run_market_scanner_crew() -> Dict[str, Any]:
    """
    Executes the 5-agent sequential workflow for the Market Trend Scanner.
    Returns the daily market intelligence briefing, specialist findings,
    and supporting sector rotation data.
    """
    try:
        llm = get_llm()
        agents = create_stock_agents(llm)
        tasks = create_market_scanner_tasks(agents)

        crew = Crew(
            agents=list(agents),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()

        task_outputs = {}
        if hasattr(crew, "tasks"):
            for t in crew.tasks:
                agent_role = getattr(t.agent, "role", "Specialist")
                output_str = str(t.output.raw) if hasattr(t, "output") and hasattr(t.output, "raw") else str(t.output)
                task_outputs[agent_role] = output_str

        sector_data = get_sector_performance()
        movers_data = get_market_movers(count=5)

        return {
            "success": True,
            "report": str(result.raw) if hasattr(result, "raw") else str(result),
            "agent_outputs": task_outputs,
            "sector_data": sector_data,
            "movers_data": movers_data,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to complete market trend scan: {str(e)}"
        }
