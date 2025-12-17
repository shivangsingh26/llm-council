"""
Prompt engineering module for LLM Council.

Provides domain-specific and complexity-aware prompt templates
to improve response quality across different research domains.
"""

from src.prompts.prompt_selector import PromptSelector

__all__ = ["PromptSelector"]
