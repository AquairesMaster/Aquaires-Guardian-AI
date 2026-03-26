 """
database.py

This module defines the abstract database interface used by Guardian House AI.
Both SQLiteDatabase and PostgresDatabase implement this interface.

The purpose of this abstraction is to:
- Allow Guardian House AI to switch databases without code changes
- Provide a consistent API for storing/loading user models and conversations
- Support future backends (MongoDB, Redis, cloud DBs, etc.)

Guardian House AI interacts ONLY with this interface, never with a specific DB.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime
from ..core.user_model import UserLifeModel


class Database(ABC):
    """
    Abstract base class for all database backends.

    Any database implementation must provide:
    - load_user_model()
    - save_user_model()
    - store_conversation()
    - load_conversation_history()
    - save_prediction()
    - close()
    """

    @abstractmethod
    def load_user_model(self, user_id: str) -> UserLifeModel | None:
        """Load the user's life model from the database."""
        pass

    @abstractmethod
    def save_user_model(self, model: UserLifeModel) -> None:
        """Persist the user's life model to the database."""
        pass

    @abstractmethod
    def store_conversation(
        self,
        user_id: str,
        message: str,
        response: str,
        emotion: Dict[str, Any],
        timestamp: datetime
    ) -> None:
        """Store a single conversation turn."""
        pass

    @abstractmethod
    def load_conversation_history(self, user_id: str, limit: int = 1000) -> list[Dict]:
        """Load recent conversation history."""
        pass

    @abstractmethod
    def save_prediction(self, prediction: Dict[str, Any]) -> None:
        """Store predictive engine outputs."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close database connection."""
        pass

