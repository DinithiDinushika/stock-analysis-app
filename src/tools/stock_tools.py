"""
Stock data fetching tools for real-time quotes, company profiles, and fundamental metrics.
Streamlined to essential, non-redundant financial metrics.
"""

import json
from typing import Dict, Any, Optional
import yfinance as yf
from crewai.tools import tool


def _safe_float(val: Any, decimals: int = 2) -> Optional[float]:
    """Safely cast value to float or return None."""
    if val is None or val == "N/A" or val == "":
        return None
    try:
        f = float(val)
        return round(f, decimals)
    except (ValueError, TypeError):
        return None


def _format_large_number(num: Optional[float]) -> str:
    """Format large numbers into Trillions, Billions, or Millions."""
    if num is None:
        return "N/A"
    try:
        val = float(num)
        if abs(val) >= 1e12:
            return f"${val / 1e12:.2f}T"
        elif abs(val) >= 1e9:
            return f"${val / 1e9:.2f}B"
        elif abs(val) >= 1e6:
            return f"${val / 1e6:.2f}M"
        return f"${val:.2f}"
    except (ValueError, TypeError):
        return "N/A"


def get_stock_quote(ticker: str) -> Dict[str, Any]:
    """
    Fetch the latest real-time stock price quote and daily movement.
    Contains only essential price, change, volume, and 52-week extremes.
    """
    ticker_clean = ticker.strip().upper()
    try:
        t = yf.Ticker(ticker_clean)
        info = t.info or {}
        fast = getattr(t, "fast_info", None)
        
        current_price = _safe_float(
            info.get("currentPrice") or info.get("regularMarketPrice") or (fast.last_price if fast else None)
        )
        prev_close = _safe_float(
            info.get("previousClose") or info.get("regularMarketPreviousClose") or (fast.previous_close if fast else None)
        )
        
        if current_price is None and prev_close is not None:
            current_price = prev_close
            
        if current_price is None:
            hist = t.history(period="5d")
            if not hist.empty:
                current_price = _safe_float(hist["Close"].iloc[-1])
                prev_close = _safe_float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price

        if current_price is None:
            return {
                "success": False,
                "ticker": ticker_clean,
                "error": f"Unable to retrieve quote data for '{ticker_clean}'. Symbol may be invalid."
            }
            
        change = round(current_price - prev_close, 2) if prev_close else 0.0
        change_pct = round((change / prev_close) * 100, 2) if prev_close and prev_close > 0 else 0.0

        return {
            "success": True,
            "ticker": ticker_clean,
            "company_name": info.get("shortName") or info.get("longName") or ticker_clean,
            "current_price": current_price,
            "previous_close": prev_close,
            "change": change,
            "change_percent": change_pct,
            "volume": int(info.get("volume") or (fast.last_volume if fast else 0) or 0),
            "fifty_two_week_high": _safe_float(info.get("fiftyTwoWeekHigh") or (fast.year_high if fast else None)),
            "fifty_two_week_low": _safe_float(info.get("fiftyTwoWeekLow") or (fast.year_low if fast else None)),
            "currency": info.get("currency", "USD"),
        }

    except Exception as e:
        return {
            "success": False,
            "ticker": ticker_clean,
            "error": f"Error fetching quote for {ticker_clean}: {str(e)}"
        }


def get_company_profile(ticker: str) -> Dict[str, Any]:
    """
    Fetch company background information: name, sector, industry, and concise summary.
    """
    ticker_clean = ticker.strip().upper()
    try:
        t = yf.Ticker(ticker_clean)
        info = t.info or {}
        return {
            "success": True,
            "ticker": ticker_clean,
            "name": info.get("longName") or info.get("shortName") or ticker_clean,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "summary": info.get("longBusinessSummary", "No summary available.")[:350] + "...",
        }
    except Exception as e:
        return {
            "success": False,
            "ticker": ticker_clean,
            "error": f"Error fetching company profile: {str(e)}"
        }


def get_fundamental_metrics(ticker: str) -> Dict[str, Any]:
    """
    Fetch essential fundamental metrics:
    - Valuation: Market Capitalization, P/E Ratio
    - Profitability: Earnings Per Share (EPS), Profit Margin (%)
    - Risk & Solvency: Debt-to-Equity, Beta
    Prioritizes Alpha Vantage Company Overview API if configured, with graceful fallback to Yahoo Finance.
    """
    import os
    import requests
    ticker_clean = ticker.strip().upper()
    av_key = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()

    # 1. Attempt Alpha Vantage Overview API
    if av_key:
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_clean}&apikey={av_key}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if "MarketCapitalization" in data and data.get("Symbol") == ticker_clean:
                    mkt_cap = _safe_float(data.get("MarketCapitalization"))
                    pm = _safe_float(data.get("ProfitMargin"))
                    return {
                        "success": True,
                        "ticker": ticker_clean,
                        "source": "Alpha Vantage Company Overview",
                        "company_name": data.get("Name", ticker_clean),
                        "market_cap": _format_large_number(mkt_cap),
                        "pe_ratio": _safe_float(data.get("PERatio")),
                        "eps": _safe_float(data.get("EPS")),
                        "profit_margin_pct": round(pm * 100, 2) if pm is not None else None,
                        "debt_to_equity": _safe_float(data.get("DebtToEquityRatio")),
                        "beta": _safe_float(data.get("Beta")),
                    }
        except Exception:
            pass  # Fallback to yfinance

    # 2. Fallback to open yfinance data
    try:
        t = yf.Ticker(ticker_clean)
        info = t.info or {}
        
        market_cap_raw = info.get("marketCap")
        profit_margin = info.get("profitMargins")
        profit_margin_pct = _safe_float(profit_margin * 100) if profit_margin is not None else None

        metrics = {
            "success": True,
            "ticker": ticker_clean,
            "source": "Open Financial Feed",
            "company_name": info.get("longName") or info.get("shortName") or ticker_clean,
            "market_cap": _format_large_number(market_cap_raw),
            "pe_ratio": _safe_float(info.get("trailingPE") or info.get("forwardPE")),
            "eps": _safe_float(info.get("trailingEps")),
            "profit_margin_pct": profit_margin_pct,
            "debt_to_equity": _safe_float(info.get("debtToEquity")),
            "beta": _safe_float(info.get("beta")),
        }
        return metrics

    except Exception as e:
        return {
            "success": False,
            "ticker": ticker_clean,
            "error": f"Error fetching fundamental metrics: {str(e)}"
        }


# ==========================================
# CrewAI Tool Wrappers
# ==========================================

@tool("Get Stock Quote Tool")
def get_stock_quote_tool(ticker: str) -> str:
    """
    Retrieves the current stock quote: price, daily change %, volume, 
    and 52-week high/low for a given stock ticker symbol.
    """
    data = get_stock_quote(ticker)
    return json.dumps(data, indent=2)


@tool("Get Fundamental Financial Metrics Tool")
def get_fundamental_metrics_tool(ticker: str) -> str:
    """
    Retrieves the core fundamental financial metrics for a stock ticker:
    Market Capitalization, P/E Ratio, Earnings Per Share (EPS), Profit Margin (%), 
    Debt-to-Equity ratio, and Beta.
    """
    data = get_fundamental_metrics(ticker)
    return json.dumps(data, indent=2)


@tool("Get Company Profile Tool")
def get_company_profile_tool(ticker: str) -> str:
    """
    Retrieves company background details: sector, industry, and concise business overview.
    """
    data = get_company_profile(ticker)
    return json.dumps(data, indent=2)
