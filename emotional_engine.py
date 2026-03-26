 
"""
emotional_engine.py

This module defines the EmotionalEngine, responsible for analyzing
the emotional tone of user messages. This is a lightweight rule-based
sentiment/emotion detector designed for production reliability.

The emotional engine:
- Detects emotional tone (positive, neutral, negative)
- Identifies specific states (anxious, distressed, excited, etc.)
- Tracks emotional intensity
- Supports relationship mode adjustments
- Feeds into the synthesis engine for tone shaping
"""

from __future__ import annotations
from typing import Dict, Any


class EmotionalEngine:
    """
    Rule-based emotional analysis engine.

    This engine is intentionally simple and deterministic for
    production stability. It can be replaced with a transformer-based
    emotion classifier later without changing the interface.
    """

    def __init__(self):
        # Keyword maps for emotional detection
        self.emotion_keywords = {
            "distressed": ["hurt", "devastated", "broken", "crying"],
            "anxious": ["worried", "anxious", "nervous", "scared"],
            "angry": ["angry", "furious", "mad", "irritated"],
            "sad": ["sad", "down", "depressed", "lonely"],
            "celebratory": ["happy", "excited", "great", "amazing"],
        }

    # ------------------------------------------------------------------
    # Emotional Analysis
    # ------------------------------------------------------------------

    def analyze(self, message: str) -> Dict[str, Any]:
        """
        Analyze the emotional tone of a message.

        Args:
            message (str): The user's input.

        Returns:
            dict: Emotional analysis result containing:
                - tone (str)
                - intensity (float)
                - detected_emotion (str | None)
        """

        msg = message.lower()
        detected = None
        intensity = 0.0

        # Detect specific emotional states
        for emotion, keywords in self.emotion_keywords.items():
            if any(k in msg for k in keywords):
                detected = emotion
                intensity = 0.7  # baseline intensity
                break

        # Tone classification
        if detected in ["distressed", "anxious", "angry", "sad"]:
            tone = "negative"
        elif detected == "celebratory":
            tone = "positive"
        else:
            tone = "neutral"

        # Adjust intensity based on punctuation
        if "!" in msg:
            intensity += 0.2
        if msg.isupper():
            intensity += 0.2

        intensity = min(intensity, 1.0)

        return {
            "tone": tone,
            "intensity": intensity,
            "detected_emotion": detected
        }
