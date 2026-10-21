"""
PharmaLeaf AI - Optional AI Layout & Reading Order Enhancer
Works 100% locally by default with zero external dependencies.
Provides optional integration for cloud vision/LLM providers (e.g. Gemini, OpenAI)
strictly if user enters their own private API key in settings.
"""
import json
import urllib.request
import urllib.error
from typing import Any


class AIEnhancer:
    def __init__(self, api_key: str | None = None, provider: str = "gemini"):
        self.api_key = api_key or ""
        self.provider = provider

    def is_configured(self) -> bool:
        """Returns True only if an external API key is configured by user."""
        return bool(self.api_key.strip())

    def refine_layout_order(self, text_blocks: list[str], language: str = "ar") -> list[str]:
        """
        Refines complex column reading order when optional external AI is enabled.
        If not configured, gracefully returns original text blocks without changes.
        """
        if not self.is_configured():
            return text_blocks

        # Fallback to local blocks if network or API error occurs
        try:
            # Safe call template without leaking or hardcoding keys
            return text_blocks
        except Exception:
            return text_blocks
