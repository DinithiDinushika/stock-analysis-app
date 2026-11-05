"""
Market trend scanner tools: tracks Top Gainers, Top Losers, Most Actively traded equities,
and SPDR Sector ETF performance for macro breadth and rotation analysis.
"""

import json
from typing import Dict, Any, List
import yfinance as yf
from crewai.tools import tool

# Curated high-volume liquid equities for resilient mover scanning
ACTIVE_UNIVERSE = [
    "NVDA", "TSLA", "AAPL", "MSFT", "AMD", "AMZN", "GOOGL", "META",
    "PLTR", "COIN", "SMCI", "ARM", "MARA", "NFLX", "BA", "DIS",
    "INTC", "QCOM", "AVGO", "JPM", "XOM", "LLY", "UNH", "SOFI"
]

# Major SPDR Sector ETFs representing the 11 GICS sectors
SECTOR_ETFS = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLI": "Industrials",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLU": "Utilities",
    "XLRE": "Real Estate",
    "XLC": "Communication Services",
    "XLB": "Materials"
}


def _safe_float(val: Any, decimals: int = 2):
    try:
        return round(float(val), decimals) if val is not None else None
    except (ValueError, TypeError):
        return None


def get_market_movers(count: int = 5) -> Dict[str, Any]:
    """
    Fetch top gaining, top losing, and most active equities.
    First attempts Yahoo Finance predefined screeners; falls back to live active universe scanning.
    """
    gainers: List[Dict[str, Any]] = []
    losers: List[Dict[str, Any]] = []
    most_active: List[Dict[str, Any]] = []

    # 1. Attempt yf.screen
    try:
        if hasattr(yf, "screen"):
            g_res = yf.screen("day_gainers", count=count)
            l_res = yf.screen("day_losers", count=count)
            a_res = yf.screen("most_actives", count=count)

            def _parse_quotes(quotes_list):
                results = []
                for q in quotes_list[:count]:
                    sym = q.get("symbol")
                    if not sym:
                        continue
                    results.append({
                        "ticker": sym,
                        "name": q.get("shortName") or q.get("longName") or sym,
                        "price": _safe_float(q.get("regularMarketPrice")),
                        "change": _safe_float(q.get("regularMarketChange")),
                        "change_percent": _safe_float(q.get("regularMarketChangePercent")),
                        "volume": int(q.get("regularMarketVolume", 0) or 0)
                    })
                return results

            if "quotes" in g_res and g_res["quotes"]:
                gainers = _parse_quotes(g_res["quotes"])
            if "quotes" in l_res and l_res["quotes"]:
                losers = _parse_quotes(l_res["quotes"])
            if "quotes" in a_res and a_res["quotes"]:
                most_active = _parse_quotes(a_res["quotes"])
    except Exception:
        pass

    # 2. Resilient fallback: Scan our active universe
    if not gainers or not losers:
        universe_data = []
        try:
            # Batch download 5-day prices to calculate latest change
            tickers_str = " ".join(ACTIVE_UNIVERSE)
            data = yf.download(tickers_str, period="5d", progress=False, group_by="ticker")
            
            for ticker in ACTIVE_UNIVERSE:
                try:
                    df = data[ticker] if ticker in data else None
                    if df is not None and not df.empty and len(df) >= 2:
                        close_today = float(df["Close"].iloc[-1])
                        close_prev = float(df["Close"].iloc[-2])
                        vol = int(df["Volume"].iloc[-1])
                        chg = close_today - close_prev
                        chg_pct = (chg / close_prev) * 100
                        universe_data.append({
                            "ticker": ticker,
                            "name": ticker,
                            "price": round(close_today, 2),
                            "change": round(chg, 2),
                            "change_percent": round(chg_pct, 2),
                            "volume": vol
                        })
                except Exception:
                    continue

            if universe_data:
                # Sort by percentage change
                sorted_by_change = sorted(universe_data, key=lambda x: x["change_percent"], reverse=True)
                gainers = sorted_by_change[:count]
                losers = sorted(universe_data, key=lambda x: x["change_percent"])[:count]
                most_active = sorted(universe_data, key=lambda x: x["volume"], reverse=True)[:count]
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to retrieve market movers: {str(e)}",
                "gainers": [],
                "losers": [],
                "most_active": []
            }

    return {
        "success": True,
        "gainers": gainers,
        "losers": losers,
        "most_active": most_active
    }


def get_sector_performance() -> Dict[str, Any]:
    """
    Fetches performance metrics for all 11 SPDR Sector ETFs to analyze macro market breadth.
    """
    sector_results = []
    try:
        tickers_str = " ".join(SECTOR_ETFS.keys()) + " SPY QQQ"
        data = yf.download(tickers_str, period="5d", progress=False, group_by="ticker")
        
        for etf, sector_name in SECTOR_ETFS.items():
            try:
                df = data[etf] if etf in data else None
                if df is not None and len(df) >= 2:
                    today_close = float(df["Close"].iloc[-1])
                    prev_close = float(df["Close"].iloc[-2])
                    chg_pct = round(((today_close - prev_close) / prev_close) * 100, 2)
                    sector_results.append({
                        "symbol": etf,
                        "sector": sector_name,
                        "price": round(today_close, 2),
                        "change_percent": chg_pct,
                        "status": "Green" if chg_pct >= 0 else "Red"
                    })
            except Exception:
                continue
                
        # Sort by best performing sector
        sector_results.sort(key=lambda x: x["change_percent"], reverse=True)
        return {
            "success": True,
            "sectors": sector_results,
            "top_sector": sector_results[0] if sector_results else None,
            "lagging_sector": sector_results[-1] if sector_results else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch sector performance: {str(e)}",
            "sectors": []
        }


# ==========================================
# CrewAI Tool Wrappers
# ==========================================

@tool("Get Market Movers Tool")
def get_market_movers_tool() -> str:
    """
    Fetches the top gaining, top losing, and most active stocks in the market today,
    including their prices, daily price changes, percent changes, and trading volumes.
    """
    data = get_market_movers(count=5)
    return json.dumps(data, indent=2)


@tool("Get Sector Performance Tool")
def get_sector_performance_tool() -> str:
    """
    Fetches daily performance across the 11 major US stock market sectors (Technology, Financials, 
    Energy, Healthcare, Industrials, Consumer Discretionary/Staples, Utilities, Real Estate, etc.) 
    to evaluate market breadth and sector rotation.
    """
    data = get_sector_performance()
    return json.dumps(data, indent=2)

