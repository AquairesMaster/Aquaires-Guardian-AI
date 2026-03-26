 
"""
intent_classifier.py

This module defines the IntentClassifier, responsible for determining
the user's intent behind each message. This is a lightweight rule-based
classifier designed for production reliability, but can be replaced
with an ML model in the future.

The classifier determines whether the user is:
- Asking for information
- Seeking advice
- Requesting emotional support
- Engaging in philosophical discussion
- Triggering a specific domain (finance, health, security, etc.)
- Initiating a cross-domain query

This intent is used by:
- The router (to select agents)
- The synthesis engine (to shape the response)
- The emotional engine (to adjust tone)
"""

from __future__ import annotations
from typing import Optional, Dict, List


class IntentClassifier:
    """
    Lightweight rule-based intent classifier.

    This classifier is intentionally simple and deterministic for
    production stability. It can be replaced with a transformer-based
    classifier later without changing the interface.
    """

    def __init__(self):
        # Keyword maps for domain-specific routing
        self.domain_keywords = {
            "finance": ["money", "budget", "invest", "stocks", "crypto", "spending"],
            "health": ["health", "sleep", "diet", "doctor", "pain", "exercise"],
            "security": ["danger", "safety", "secure", "threat", "risk"],
            "learning": ["study", "learn", "school", "class", "homework"],
            "physical": ["workout", "training", "gym", "muscles", "run"],
            "supplies": ["inventory", "restock", "supplies", "order", "buy"],
        }

    # ------------------------------------------------------------------
    # Main Intent Classification
    # ------------------------------------------------------------------

    def classify(self, message: str) -> str:
        """
        Determine the user's intent based on message content.

        Args:
            message (str): The user's input.

        Returns:
            str: The classified intent.
        """

        msg = message.lower().strip()

        # Emotional support
        if any(x in msg for x in ["sad", "upset", "anxious", "stressed", "lonely"]):
            return "emotional_support"

        # Advice seeking
        if any(x in msg for x in ["should i", "what do i do", "help me decide"]):
            return "seeking_advice"

        # Philosophical discussion
        if any(x in msg for x in ["meaning of", "purpose", "life", "philosophy"]):
            return "philosophical_discussion"

        # Domain-specific routing
        for domain, keywords in self.domain_keywords.items():
            if any(k in msg for k in keywords):
                return domain

        # Information request
        if msg.startswith("what") or msg.startswith("how") or msg.endswith("?"):
            return "information_request"

        # Default: general conversation
        return "general_conversation"
