"""
Agents package for the Stock Market Intelligence Platform.
Contains specialized agents and task definitions for both single stock analysis
and market trend scanning.
"""

from src.agents.stock_agents import create_stock_agents
from src.agents.tasks import (
    create_stock_analysis_tasks,
    create_market_scanner_tasks,
)

__all__ = [
    "create_stock_agents",
    "create_stock_analysis_tasks",
    "create_market_scanner_tasks",
]

