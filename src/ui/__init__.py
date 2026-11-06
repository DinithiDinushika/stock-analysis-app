"""
UI package for the Stock Market Intelligence Platform.
Contains Plotly charts, UI cards, and presentation components.
"""

from src.ui.charts import (
    create_stock_candlestick_chart,
    create_sector_performance_chart,
)
from src.ui.components import (
    render_metric_banner,
    render_verified_badge,
    # render_disclaimer,
    render_company_header,
)

__all__ = [
    "create_stock_candlestick_chart",
    "create_sector_performance_chart",
    "render_metric_banner",
    "render_verified_badge",
    # "render_disclaimer",
    "render_company_header",
]

