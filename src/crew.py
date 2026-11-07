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


def _format_agent_error(e: Exception, action_desc: str) -> str:
    err_str = str(e)
    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
        return (
            f"⚠️ Quota Exceeded (429 RESOURCE_EXHAUSTED) while running {action_desc}.\n\n"
            "**Why this happened:** Google's Free Tier has strict daily caps on preview models "
            "(e.g., `gemini-2.5-flash` allows only 20 requests/day). A 5-agent sequential run invokes 5 requests, "
            "so 4 runs quickly exhausts that daily limit.\n\n"
            "**Fix:**\n"
            "- Switch to `gemini/gemini-2.0-flash` in your `.env` (`GEMINI_MODEL=gemini/gemini-2.0-flash`), which allows 1,500 requests/day on the Free Tier!\n"
            "- Or generate a new key under a new project in Google AI Studio."
        )
    if "404" in err_str or "NOT_FOUND" in err_str:
        return (
            f"⚠️ Model Not Found (404 NOT_FOUND) while running {action_desc}.\n\n"
            "**Why this happened:** The requested model is not supported on Google's current `v1beta` endpoint.\n\n"
            "**Fix:**\n"
            "- Set `GEMINI_MODEL=gemini/gemini-2.0-flash` in your `.env` file.\n"
            "- Ensure your Gemini API key from Google AI Studio is active."
        )
    return f"Failed to complete {action_desc}: {err_str}"


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

        return {
            "success": True,
            "ticker": ticker_clean,
            "start_date": start_date,
            "end_date": end_date,
            "report": str(result.raw) if hasattr(result, "raw") else str(result),
            "agent_outputs": task_outputs,
        }

    except Exception as e:
        return {
            "success": False,
            "ticker": ticker_clean,
            "error": _format_agent_error(e, f"stock analysis for {ticker_clean}")
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
            "error": _format_agent_error(e, "market trend scan")
        }
