 
"""
context_manager.py

This module defines the ContextManager class, which is responsible for
maintaining short-term and long-term conversational context, emotional
state history, and memory retrieval for Guardian House AI.

The ContextManager acts as the "working memory" of the system:
- Tracks recent conversation turns
- Stores emotional tone history
- Provides context windows for synthesis
- Interfaces with the database for long-term memory
- Injects the AgentRouter for multi-agent orchestration

This subsystem is essential for:
- Personalized responses
- Emotional continuity
- Cross-domain synthesis
- Predictive modeling
"""

from __future__ import annotations
from collections import deque
from datetime import datetime
from typing import Dict, Any, List, Optional

from .router import AgentRouter
from .database import Database


class ContextManager:
    """
    Manages conversational context, emotional state history, and memory.

    Attributes:
        router (AgentRouter): The routing engine for multi-agent orchestration.
        db (Database): Database backend for long-term memory.
        conversation_history (deque): Recent conversation turns.
        emotional_history (deque): Recent emotional states.
        max_history (int): Maximum number of conversation turns to keep in memory.
    """

    def __init__(
        self,
        router: AgentRouter,
        db: Database,
        max_history: int = 1000,
        max_emotions: int = 500
    ):
        self.router = router
        self.db = db

        # Short-term memory buffers
        self.conversation_history = deque(maxlen=max_history)
        self.emotional_history = deque(maxlen=max_emotions)

    # ----------------------------------------------------------------------
    # Conversation History
    # ----------------------------------------------------------------------

    def update_history(self, message: str, emotion: Dict[str, Any]) -> None:
        """
        Add a new user message and emotional state to short-term memory.

        Args:
            message (str): The user's message.
            emotion (dict): Emotional analysis result.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "emotion": emotion
        }
        self.conversation_history.append(entry)
        self.emotional_history.append(emotion)

    def get_recent_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent conversation turns.

        Args:
            limit (int): Number of turns to return.

        Returns:
            list[dict]: Recent conversation entries.
        """
        return list(self.conversation_history)[-limit:]

    # ----------------------------------------------------------------------
    # Emotional State
    # ----------------------------------------------------------------------

    def get_recent_emotional_state(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent emotional state.

        Returns:
            dict | None: The last emotional analysis result.
        """
        if not self.emotional_history:
            return None
        return self.emotional_history[-1]

    def get_emotional_trend(self, window: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve a window of recent emotional states.

        Args:
            window (int): Number of emotional states to return.

        Returns:
            list[dict]: Emotional state entries.
        """
        return list(self.emotional_history)[-window:]

    # ----------------------------------------------------------------------
    # Long-Term Memory (Database)
    # ----------------------------------------------------------------------

    def load_long_term_history(self, user_id: str, limit: int = 200) -> List[Dict]:
        """
        Load long-term conversation history from the database.

        Args:
            user_id (str): The user's ID.
            limit (int): Number of entries to load.

        Returns:
            list[dict]: Conversation entries.
        """
        return self.db.load_conversation_history(user_id, limit)

    # ----------------------------------------------------------------------
    # Embeddings (Future Expansion)
    # ----------------------------------------------------------------------

    def embed_text(self, text: str) -> List[float]:
        """
        Placeholder for embedding generation.

        In a future version, this will:
        - Generate vector embeddings
        - Support semantic search
        - Enable memory retrieval based on meaning

        Args:
            text (str): Text to embed.

        Returns:
            list[float]: Placeholder vector.
        """
        # Placeholder: return a dummy vector
        return [0.0] * 10

    # ----------------------------------------------------------------------
    # Context Retrieval for Synthesis
    # ----------------------------------------------------------------------

    def build_context_window(self, message: str, limit: int = 5) -> Dict[str, Any]:
        """
        Build a context window for the synthesis engine.

        Args:
            message (str): The current user message.
            limit (int): Number of recent turns to include.

        Returns:
            dict: Context window containing:
                - recent conversation
                - emotional trend
                - embeddings (future)
        """
        return {
            "recent_messages": self.get_recent_context(limit),
            "emotional_trend": self.get_emotional_trend(limit),
            "embedding": self.embed_text(message)
        }
