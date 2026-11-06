"""
Financial news and sentiment extraction tool.
Integrates Alpha Vantage News & Sentiment API with automatic fallback to open financial feeds.
Retrieves recent headlines, extracts summaries, and computes sentiment polarity.
"""

import os
import json
import datetime
from typing import Dict, Any, List
import requests
import yfinance as yf
from crewai.tools import tool

# Lexicon for deterministic sentiment scoring when raw text is evaluated
BULLISH_KEYWORDS = {
    "beat", "surged", "surge", "jumps", "jumped", "rally", "rallies", "growth",
    "profit", "record", "upgrade", "upgraded", "bullish", "outperform", "dividend",
    "expansion", "milestone", "breakthrough", "approval", "soars", "gain", "gains",
    "positive", "partnership", "acquisition", "strong", "higher", "exceeds"
}

BEARISH_KEYWORDS = {
    "miss", "missed", "plunge", "plunged", "drops", "dropped", "slump", "loss",
    "losses", "downgrade", "downgraded", "bearish", "underperform", "lawsuit",
    "investigation", "recession", "decline", "declines", "warning", "cuts", "debt",
    "negative", "inflation", "slashed", "fraud", "scandal", "selloff", "lower", "fall"
}


def _score_text_sentiment(text: str) -> Dict[str, Any]:
    """Score sentiment polarity of a piece of text using keyword frequency."""
    text_lower = text.lower()
    words = set(text_lower.replace(",", " ").replace(".", " ").replace(";", " ").split())
    
    bull_hits = words.intersection(BULLISH_KEYWORDS)
    bear_hits = words.intersection(BEARISH_KEYWORDS)
    
    score = len(bull_hits) - len(bear_hits)
    if score > 0:
        label = "Bullish"
    elif score < 0:
        label = "Bearish"
    else:
        label = "Neutral"
        
    return {
        "label": label,
        "score": score,
        "positive_triggers": list(bull_hits),
        "negative_triggers": list(bear_hits)
    }


def _parse_alphavantage_date(date_str: str) -> str:
    """Parse Alpha Vantage date string like 20240315T123000 to YYYY-MM-DD HH:MM."""
    try:
        dt = datetime.datetime.strptime(date_str[:13], "%Y%m%dT%H%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return date_str[:10] if len(date_str) >= 10 else "Recent"


def get_stock_news(ticker: str, limit: int = 6) -> Dict[str, Any]:
    """
    Fetch recent financial news articles and assess sentiment polarity.
    Prioritizes Alpha Vantage News & Sentiment API if ALPHA_VANTAGE_API_KEY is configured.
    Falls back gracefully to Yahoo Finance news on rate limits or missing keys.
    """
    ticker_clean = ticker.strip().upper()
    articles: List[Dict[str, Any]] = []
    source_used = "Open Feed"
    av_key = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()

    # 1. Attempt Alpha Vantage News & Sentiment API if key is present
    if av_key:
        try:
            url = (
                f"https://www.alphavantage.co/query"
                f"?function=NEWS_SENTIMENT&tickers={ticker_clean}&limit={limit}&apikey={av_key}"
            )
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # Check for successful feed output (Alpha Vantage returns 'feed' list)
                if "feed" in data and isinstance(data["feed"], list) and len(data["feed"]) > 0:
                    source_used = "Alpha Vantage News & Sentiment API"
                    for item in data["feed"][:limit]:
                        av_sentiment = item.get("overall_sentiment_label", "Neutral")
                        # Normalize label to Bullish / Bearish / Neutral
                        if "Bullish" in av_sentiment:
                            norm_sentiment = "Bullish"
                        elif "Bearish" in av_sentiment:
                            norm_sentiment = "Bearish"
                        else:
                            norm_sentiment = "Neutral"

                        time_pub = _parse_alphavantage_date(item.get("time_published", ""))
                        articles.append({
                            "title": item.get("title", ""),
                            "publisher": item.get("source", "Alpha Vantage"),
                            "published_at": time_pub,
                            "summary": item.get("summary", "")[:250] + "...",
                            "url": item.get("url", ""),
                            "sentiment": norm_sentiment,
                        })
        except Exception:
            pass  # Seamless fallback to open feed

    # 2. Fallback to open yfinance feed if Alpha Vantage is not configured or rate-limited
    if not articles:
        try:
            t = yf.Ticker(ticker_clean)
            raw_news = getattr(t, "news", []) or []
            for item in raw_news[:limit]:
                content_obj = item.get("content", {}) if "content" in item else item
                title = content_obj.get("title") or item.get("title", "")
                summary = content_obj.get("summary") or item.get("summary", "")
                publisher = (
                    content_obj.get("provider", {}).get("displayName")
                    if isinstance(content_obj.get("provider"), dict)
                    else item.get("publisher", "Financial Wire")
                )
                
                pub_time = content_obj.get("pubDate") or item.get("providerPublishTime")
                if isinstance(pub_time, (int, float)):
                    pub_str = datetime.datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M")
                elif isinstance(pub_time, str):
                    pub_str = pub_time[:16].replace("T", " ")
                else:
                    pub_str = "Recent"

                canonical = content_obj.get("canonicalUrl", {})
                url = canonical.get("url", "") if isinstance(canonical, dict) else item.get("link", "")

                text_to_eval = f"{title}. {summary}"
                sentiment = _score_text_sentiment(text_to_eval)

                articles.append({
                    "title": title,
                    "publisher": publisher,
                    "published_at": pub_str,
                    "summary": summary[:250] + ("..." if len(summary) > 250 else ""),
                    "url": url,
                    "sentiment": sentiment["label"]
                })
        except Exception as e:
            return {
                "success": False,
                "ticker": ticker_clean,
                "error": f"Error retrieving news for {ticker_clean}: {str(e)}",
                "articles": []
            }

    # Aggregate sentiment breakdown
    bullish_count = sum(1 for a in articles if a["sentiment"] == "Bullish")
    bearish_count = sum(1 for a in articles if a["sentiment"] == "Bearish")
    neutral_count = len(articles) - (bullish_count + bearish_count)

    if bullish_count > bearish_count:
        overall = "Bullish"
    elif bearish_count > bullish_count:
        overall = "Bearish"
    else:
        overall = "Neutral"

    return {
        "success": True,
        "ticker": ticker_clean,
        "source": source_used,
        "total_articles": len(articles),
        "overall_sentiment": overall,
        "sentiment_breakdown": {
            "bullish_articles": bullish_count,
            "bearish_articles": bearish_count,
            "neutral_articles": neutral_count
        },
        "articles": articles
    }


# ==========================================
# CrewAI Tool Wrapper
# ==========================================

@tool("Get Stock News and Sentiment Tool")
def get_stock_news_tool(ticker: str) -> str:
    """
    Fetches the latest news headlines, publication dates, summaries, and sentiment polarity 
    for a given stock ticker symbol using Alpha Vantage News & Sentiment API (with automatic fallback).
    Helps identify catalysts, earnings surprises, and corporate developments.
    """
    data = get_stock_news(ticker, limit=6)
    return json.dumps(data, indent=2)
