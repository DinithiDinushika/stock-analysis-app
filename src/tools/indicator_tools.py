"""
Deterministic technical analysis and quantitative indicators calculation engine.
Streamlined strictly to essential metrics: RSI, MACD, Moving Averages (50 & 200 SMA),
Historical Volatility, and Maximum Drawdown.
"""

import json
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import yfinance as yf
from crewai.tools import tool


def get_historical_ohlcv(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical Open, High, Low, Close, Volume data for a given ticker.
    Supported periods: '1mo', '3mo', '6mo', '1y', '2y', '5y'.
    """
    ticker_clean = ticker.strip().upper()
    valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
    if period not in valid_periods:
        period = "1y"

    t = yf.Ticker(ticker_clean)
    df = t.history(period=period, interval=interval)
    
    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    elif "Datetime" in df.columns:
        df["Date"] = pd.to_datetime(df["Datetime"]).dt.tz_localize(None)

    df.set_index("Date", inplace=True)
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan
            
    return df[required_cols].dropna(subset=["Close"])


def calculate_technical_indicators(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Calculates the essential technical and risk indicators:
    1. Trend: 50-day SMA & 200-day SMA (Golden / Death Cross)
    2. Momentum: RSI (14 periods)
    3. Trend Momentum: MACD (12, 26, 9)
    4. Risk / Volatility: 30-Day Annualized Volatility (%)
    5. Downside Risk: Maximum Drawdown (%)
    """
    if df.empty or len(df) < 14:
        return df, {"success": False, "error": "Insufficient historical data for technical calculations."}

    df = df.copy()
    close = df["Close"]

    # 1. Moving Averages (50 & 200 SMA for medium and long-term trend)
    df["SMA_50"] = close.rolling(window=50, min_periods=1).mean()
    df["SMA_200"] = close.rolling(window=200, min_periods=1).mean()

    # 2. Relative Strength Index (RSI - 14 periods) via Wilder's Smoothing
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI_14"] = 100 - (100 / (1 + rs))
    df["RSI_14"] = df["RSI_14"].fillna(50.0)

    # 3. MACD (12, 26, 9)
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # 4. Historical Volatility (30-day annualized)
    daily_returns = close.pct_change()
    rolling_30d_vol = daily_returns.rolling(window=30, min_periods=10).std() * np.sqrt(252) * 100
    df["Volatility_30D"] = rolling_30d_vol

    # 5. Maximum Drawdown Calculation
    rolling_max = close.cummax()
    drawdown = (close - rolling_max) / rolling_max * 100
    df["Drawdown_Pct"] = drawdown
    max_drawdown = round(float(drawdown.min()), 2)

    # Latest Values
    latest = df.iloc[-1]
    latest_close = round(float(latest["Close"]), 2)
    latest_rsi = round(float(latest["RSI_14"]), 2)
    latest_macd = round(float(latest["MACD"]), 3)
    latest_signal = round(float(latest["MACD_Signal"]), 3)
    latest_hist = round(float(latest["MACD_Hist"]), 3)
    latest_sma50 = round(float(latest["SMA_50"]), 2)
    latest_sma200 = round(float(latest["SMA_200"]), 2) if not np.isnan(latest["SMA_200"]) else None
    latest_vol = round(float(latest["Volatility_30D"]), 2) if not np.isnan(latest["Volatility_30D"]) else None

    # Automated Indicator Interpretation
    if latest_rsi >= 70:
        rsi_signal = "Overbought (> 70)"
    elif latest_rsi <= 30:
        rsi_signal = "Oversold (< 30)"
    else:
        rsi_signal = "Neutral (30-70)"

    macd_signal = "Bullish (Above Signal)" if latest_macd > latest_signal else "Bearish (Below Signal)"

    if latest_sma200 is not None:
        if latest_close > latest_sma50 > latest_sma200:
            trend_status = "Bullish Uptrend (Price > SMA50 > SMA200)"
        elif latest_close < latest_sma50 < latest_sma200:
            trend_status = "Bearish Downtrend (Price < SMA50 < SMA200)"
        else:
            trend_status = "Consolidation / Mixed"
    else:
        trend_status = "Bullish" if latest_close > latest_sma50 else "Bearish"

    summary = {
        "success": True,
        "latest_close": latest_close,
        "rsi_14": latest_rsi,
        "rsi_signal": rsi_signal,
        "macd": latest_macd,
        "macd_signal": latest_signal,
        "macd_histogram": latest_hist,
        "macd_status": macd_signal,
        "sma_50": latest_sma50,
        "sma_200": latest_sma200,
        "trend_status": trend_status,
        "annualized_volatility_30d_pct": latest_vol,
        "max_drawdown_pct": max_drawdown,
    }

    return df, summary


# ==========================================
# CrewAI Tool Wrapper
# ==========================================

@tool("Get Technical Analysis and Indicators Tool")
def get_technical_analysis_tool(ticker: str, period: str = "1y") -> str:
    """
    Computes essential technical indicators for a given stock ticker over a period ('1mo', '3mo', '6mo', '1y', '5y').
    Returns exact numbers for RSI (14), MACD (12, 26, 9), SMA 50, SMA 200, 
    30-Day Annualized Volatility (%), and Maximum Drawdown (%).
    """
    df = get_historical_ohlcv(ticker, period=period)
    if df.empty:
        return json.dumps({
            "success": False,
            "error": f"No historical price data found for ticker '{ticker}'."
        })

    _, summary = calculate_technical_indicators(df)
    summary["ticker"] = ticker.upper()
    summary["period_analyzed"] = period
    return json.dumps(summary, indent=2)
