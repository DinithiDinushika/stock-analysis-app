"""
Interactive Plotly charts for stock price action, technical indicators, and sector performance.
"""

from typing import List, Dict, Any
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_stock_candlestick_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """
    Creates an interactive 3-panel Plotly financial chart:
    - Panel 1 (Height 60%): Candlestick price chart with 50 SMA and 200 SMA overlays
    - Panel 2 (Height 20%): Volume bar chart with color-coded buying/selling pressure
    - Panel 3 (Height 20%): RSI (14) indicator with 70/30 overbought/oversold boundaries
    """
    if df.empty or len(df) < 5:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data to render chart",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig

    # Create 3-row subplot
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.60, 0.20, 0.20],
        subplot_titles=(
            f"{ticker.upper()} Price Action & Moving Averages",
            "Trading Volume",
            "Relative Strength Index (RSI 14)"
        )
    )

    dates = df.index

    # 1. Candlestick Price Trace
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350"
        ),
        row=1, col=1
    )

    # 50-Day SMA Overlay
    if "SMA_50" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=df["SMA_50"],
                mode="lines",
                name="50 SMA",
                line=dict(color="#f39c12", width=1.5)
            ),
            row=1, col=1
        )

    # 200-Day SMA Overlay
    if "SMA_200" in df.columns:
        valid_200 = df["SMA_200"].dropna()
        if not valid_200.empty:
            fig.add_trace(
                go.Scatter(
                    x=valid_200.index,
                    y=valid_200,
                    mode="lines",
                    name="200 SMA",
                    line=dict(color="#3498db", width=2)
                ),
                row=1, col=1
            )

    # 2. Volume Bars
    vol_colors = [
        "#26a69a" if c >= o else "#ef5350"
        for c, o in zip(df["Close"], df["Open"])
    ]
    fig.add_trace(
        go.Bar(
            x=dates,
            y=df["Volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.8
        ),
        row=2, col=1
    )

    # 3. RSI (14)
    if "RSI_14" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=df["RSI_14"],
                mode="lines",
                name="RSI 14",
                line=dict(color="#9b59b6", width=1.5)
            ),
            row=3, col=1
        )

        # Overbought (70) and Oversold (30) Reference Lines
        fig.add_hline(
            y=70, line_dash="dash", line_color="rgba(239, 83, 80, 0.6)",
            line_width=1, row=3, col=1,
            annotation_text="Overbought (70)", annotation_position="top right",
            annotation_font=dict(size=10, color="#ef5350")
        )
        fig.add_hline(
            y=30, line_dash="dash", line_color="rgba(38, 166, 154, 0.6)",
            line_width=1, row=3, col=1,
            annotation_text="Oversold (30)", annotation_position="bottom right",
            annotation_font=dict(size=10, color="#26a69a")
        )

    # Layout styling
    fig.update_layout(
        height=680,
        margin=dict(l=40, r=40, t=40, b=20),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )

    # Format Y axes
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[10, 90], row=3, col=1)

    return fig


def create_sector_performance_chart(sectors: List[Dict[str, Any]]) -> go.Figure:
    """
    Creates an interactive horizontal bar chart ranking the 11 US SPDR Sectors by daily performance.
    Green bars indicate gaining sectors, red bars indicate contracting sectors.
    """
    if not sectors:
        fig = go.Figure()
        fig.add_annotation(text="No sector data available", showarrow=False)
        return fig

    # Sort sectors ascending so best is on top of horizontal chart
    sorted_sectors = sorted(sectors, key=lambda x: x.get("change_percent", 0))

    names = [f"{s.get('sector', '')} ({s.get('symbol', '')})" for s in sorted_sectors]
    changes = [s.get("change_percent", 0) for s in sorted_sectors]
    colors = ["#26a69a" if val >= 0 else "#ef5350" for val in changes]

    fig = go.Figure(
        go.Bar(
            x=changes,
            y=names,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{val:+.2f}%" for val in changes],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="<b>S&P 500 Sector Performance Heatmap (11 Sectors)</b>",
        xaxis_title="Daily Change (%)",
        height=450,
        margin=dict(l=20, r=20, t=50, b=30),
        template="plotly_white",
        hovermode="y",
    )
    fig.add_vline(x=0, line_width=1, line_color="#888888")

    return fig

