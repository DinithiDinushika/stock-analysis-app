"""
Financial news and sentiment extraction tool.
Retrieves recent headlines, extracts summaries, and computes deterministic sentiment polarity.
Supports Yahoo Finance news and optional Finnhub News API integration.
"""

import os
import json
import datetime
from typing import Dict, Any, List
import requests
import yfinance as yf
from crewai.tools import tool

# Lexicon for deterministic sentiment scoring
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


def get_stock_news(ticker: str, limit: int = 8) -> Dict[str, Any]:
    """
    Fetch recent financial news articles and assess sentiment polarity.
    Attempts Finnhub API if configured, otherwise defaults to Yahoo Finance news.
    """
    ticker_clean = ticker.strip().upper()
    articles: List[Dict[str, Any]] = []
    finnhub_key = os.getenv("FINNHUB_API_KEY", "")

    # 1. Attempt Finnhub if key is present
    if finnhub_key:
        try:
            today = datetime.date.today()
            from_date = (today - datetime.timedelta(days=14)).isoformat()
            to_date = today.isoformat()
            url = f"https://finnhub.io/api/v1/company-news?symbol={ticker_clean}&from={from_date}&to={to_date}&token={finnhub_key}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                raw_articles = resp.json()
                for item in raw_articles[:limit]:
                    headline = item.get("headline", "")
                    summary = item.get("summary", "")
                    content = f"{headline}. {summary}"
                    sentiment = _score_text_sentiment(content)
                    
                    published_dt = datetime.datetime.fromtimestamp(item.get("datetime", 0)).strftime("%Y-%m-%d %H:%M")
                    articles.append({
                        "title": headline,
                        "publisher": item.get("source", "Finnhub"),
                        "published_at": published_dt,
                        "summary": summary[:250] + ("..." if len(summary) > 250 else ""),
                        "url": item.get("url", ""),
                        "sentiment": sentiment["label"]
                    })
        except Exception:
            pass  # Fallback to yfinance

    # 2. Fallback to yfinance news
    if not articles:
        try:
            t = yf.Ticker(ticker_clean)
            raw_news = getattr(t, "news", []) or []
            for item in raw_news[:limit]:
                # yfinance nested format support
                content_obj = item.get("content", {}) if "content" in item else item
                title = content_obj.get("title") or item.get("title", "")
                summary = content_obj.get("summary") or item.get("summary", "")
                publisher = (
                    content_obj.get("provider", {}).get("displayName")
                    if isinstance(content_obj.get("provider"), dict)
                    else item.get("publisher", "Yahoo Finance")
                )
                
                # Timestamp parsing
                pub_time = content_obj.get("pubDate") or item.get("providerPublishTime")
                if isinstance(pub_time, (int, float)):
                    pub_str = datetime.datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M")
                elif isinstance(pub_time, str):
                    pub_str = pub_time[:16].replace("T", " ")
                else:
                    pub_str = "Recent"

                # Link
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

    # Aggregate sentiment
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
    for a given stock ticker symbol. Helps identify catalysts, earnings beats/misses, and corporate developments.
    """
    data = get_stock_news(ticker, limit=6)
    return json.dumps(data, indent=2)

