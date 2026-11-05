"""
Crew orchestration engine for the Stock Market Intelligence Platform.
Manages Crew instantiation and execution for both Single Stock Deep-Dive
and Market Trend Scanner workflows.
"""

from typing import Dict, Any, Optional
from crewai import Crew, Process
from src.config import get_llm
from src.agents.stock_agents import create_stock_agents
from src.agents.tasks import (
    create_stock_analysis_tasks,
    create_market_scanner_tasks,
)


def run_stock_analysis_crew(ticker: str, period: str = "1y") -> Dict[str, Any]:
    """
    Executes the 5-agent sequential workflow for a single stock ticker.
    Returns the final synthesized dossier and intermediate agent outputs.
    """
    ticker_clean = ticker.strip().upper()
    try:
        llm = get_llm()
        agents = create_stock_agents(llm)
        tasks = create_stock_analysis_tasks(ticker_clean, period, agents)

        crew = Crew(
            agents=list(agents),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        
        # Extract task outputs if available for tabbed UI presentation
        task_outputs = {}
        if hasattr(crew, "tasks"):
            for t in crew.tasks:
                agent_role = getattr(t.agent, "role", "Specialist")
                output_str = str(t.output.raw) if hasattr(t, "output") and hasattr(t.output, "raw") else str(t.output)
                task_outputs[agent_role] = output_str

        return {
            "success": True,
            "ticker": ticker_clean,
            "period": period,
            "report": str(result.raw) if hasattr(result, "raw") else str(result),
            "agent_outputs": task_outputs,
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
    Returns the daily market intelligence briefing and specialist findings.
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

        return {
            "success": True,
            "report": str(result.raw) if hasattr(result, "raw") else str(result),
            "agent_outputs": task_outputs,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to complete market trend scan: {str(e)}"
        }

