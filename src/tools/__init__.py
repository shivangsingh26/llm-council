"""
Tools module for LLM Council.

Provides real-world data access through various APIs:
- Financial data (Yahoo Finance)
- Sports data (TheSportsDB)
- Shopping data (product APIs)
- Healthcare data (OpenFDA, PubMed)
- Web search (Tavily)
"""

from src.tools.finance_api import FinanceAPI

__all__ = ["FinanceAPI"]
