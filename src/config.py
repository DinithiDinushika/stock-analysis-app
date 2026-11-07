"""
Configuration settings and environment setup for the Stock Market Intelligence Platform.
Configured exclusively for Google Gemini models.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-2.0-flash")

# Alpha Vantage Configuration (Used for News Sentiment & Company Overview)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")


def get_llm():
    """
    Initializes and returns the CrewAI LLM instance using Google Gemini.
    """
    from crewai import LLM
    
    if not GEMINI_API_KEY:
        raise ValueError(
            "Missing GEMINI_API_KEY. Please provide your Google Gemini API key in the .env file."
        )
        
    return LLM(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.2
    )
