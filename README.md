# 🤖 MarketMind AI: Autonomous Multi-Agent Stock Market Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-orange.svg)](https://www.crewai.com/)
[![LLM](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4.svg)](https://aistudio.google.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)

An **Agentic AI Financial Intelligence Platform** that orchestrates a collaborative committee of **5 specialized LLM agents** to autonomously retrieve real-time market data, compute quantitative indicators, analyze corporate fundamentals, track news sentiment, audit downside risks, and author institutional-grade investment briefs.

---

## 🏛️ Agentic AI Architecture: The Worker–Critic–Synthesizer Pattern

Rather than relying on a monolithic prompt or brittle sequential chain, MarketMind AI implements a hierarchical **Worker–Critic–Synthesizer** multi-agent architecture powered by **CrewAI** and **Google Gemini**:

```
                       [ User Input / Goal ]
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
[ Technical Analyst ]   [ Fundamental Analyst ]   [ News & Sentiment Analyst ]
  (Momentum Worker)       (Valuation Worker)          (Catalyst Worker)
   tools: RSI, MACD,       tools: P/E, EPS,            tools: News Search,
   50/200 SMA, Drawdown    Solvency, Margins           Sentiment Polarity
     │                           │                           │
     └───────────────────────────┼───────────────────────────┘
                                 ▼
                    [ Risk & Compliance Auditor ]
                     (Adversarial Critic Agent)
                     • Independent thesis stress-test
                     • Numerical fact-check against raw data
                     • Formulates the Bear Case
                                 │
                                 ▼
                   [ Chief Investment Strategist ]
                     (Lead Synthesizer Agent)
                     • Aggregates specialist evidence
                     • Assigns conviction score (1-10)
                     • Authors final Investment Dossier
                                 │
                                 ▼
                 [ Interactive UI & PDF/Markdown Export ]
```

---

## 👥 The 5 Specialized Domain Agents

| # | Agent Name | Archetype | Tools Assigned | Core Responsibility |
|---|---|---|---|---|
| **1** | **Technical Analyst** | Worker | `indicators_tool`, `quote_tool` | Computes RSI (14), MACD (12, 26, 9), 50 & 200 SMAs, 30-day volatility, and historical Maximum Drawdown via deterministic math. |
| **2** | **Fundamental Analyst** | Worker | `fundamentals_tool`, `profile_tool` | Evaluates Market Cap, P/E ratio, Diluted EPS, Profit Margin %, and balance sheet Debt-to-Equity solvency. |
| **3** | **News Analyst** | Worker | `news_tool`, `movers_tool` | Identifies breaking catalysts, executive announcements, and computes net sentiment polarity (Bullish, Bearish, or Neutral). |
| **4** | **Risk Auditor** | Critic | *Zero Tools (Cognitive Critic)* | Acts as an objective adversary: challenges the bull thesis, verifies numbers match ground-truth facts, and constructs the Bear Case. |
| **5** | **Chief Strategist** | Synthesizer | *Zero Tools (Lead Reporter)* | Weighs specialist findings, assigns an Informational Outlook (Bullish / Neutral / Bearish), and authors the final publication-ready brief. |

---

## 🔁 Symmetrical Dual-Mode Workflows

The exact same 5 domain agents power **both** workflows without code duplication:

### Workflow A: Single Stock Deep-Dive
1. **Technical Worker**: Evaluates momentum, trend alignment (Golden/Death Cross), and drawdown.
2. **Fundamental Worker**: Audits valuation multiples and corporate solvency.
3. **News Worker**: Extracts recent headlines and determines market sentiment.
4. **Risk Critic**: Cross-checks numbers against tool facts and builds the Bear Case.
5. **Strategist**: Synthesizes the **Executive Investment Dossier**.

### Workflow B: Market Trend Scanner
1. **News Worker**: Discovers today's Top Gainers and Losers and explains **why** they moved using breaking news.
2. **Technical Worker**: Ranks the 11 S&P 500 sectors to diagnose market breadth (Risk-On vs. Defensive).
3. **Fundamental Worker**: Screens moving stocks to separate real earnings rallies from speculative penny-stock hype.
4. **Risk Critic**: Flags low-float traps, short-squeeze volatility, and sector contagion.
5. **Strategist**: Authors the **Daily Market Trend Briefing**.

---

## 🛡️ Anti-Hallucination & Deterministic Data Layer

A critical design principle of this platform is the strict separation of **Deterministic Math** from **LLM Reasoning**:
- **Zero Math Hallucination**: LLMs never compute RSI, moving averages, or drawdowns. Indicators are calculated deterministically in Python using `pandas` and `numpy`.
- **Fact-Checking Gatekeeper**: The Risk Auditor reviews claims against verified tool outputs before the Chief Strategist synthesizes the dossier.
- **Trust Badges**: Visual indicators clearly distinguish verified financial figures from qualitative AI interpretations.

---

## 🚀 Quick Setup & Installation

### 1. Clone & Enter Directory
```bash
git clone <your-repo-url>
cd Stock-market-analysis-app
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure API Keys
Copy the example environment file and add your Google Gemini API key:
```powershell
Copy-Item .env.example .env
```
Inside `.env`:
```env
GEMINI_API_KEY=AIzaSy...your_gemini_api_key
GEMINI_MODEL=gemini/gemini-2.5-flash

# Alpha Vantage (Used for News Sentiment & Company Overview)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```
*(Get a free Gemini key at [Google AI Studio](https://aistudio.google.com/) and free Alpha Vantage key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)).*

### 5. Launch the Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

