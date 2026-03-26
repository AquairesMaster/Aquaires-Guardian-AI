 
"""
db_sqlite.py

SQLite implementation of the Database interface.

This backend is ideal for:
- Local development
- Mobile or embedded deployments
- Offline-first systems
- Single-user environments

SQLite stores JSON strings for Pydantic models.
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any
from pydantic import ValidationError
from .database import Database
from .user_model import UserLifeModel


class SQLiteDatabase(Database):
    """
    SQLite implementation of the Guardian House database layer.
    """

    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self) -> None:
        """Create required tables if they do not exist."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_model (
                user_id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                message TEXT,
                response TEXT,
                emotion TEXT,
                timestamp TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction JSON
            )
        """)

        self.conn.commit()

    # ---------------------------------------------------------
    # User Model
    # ---------------------------------------------------------

    def load_user_model(self, user_id: str) -> UserLifeModel | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM user_model WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return None

        try:
            return UserLifeModel.model_validate_json(row["data"])
        except ValidationError:
            return None

    def save_user_model(self, model: UserLifeModel) -> None:
        cursor = self.conn.cursor()
        json_data = model.model_dump_json()

        cursor.execute("""
            INSERT INTO user_model (user_id, data)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET data=excluded.data
        """, (model.user_id, json_data))

        self.conn.commit()

    # ---------------------------------------------------------
    # Conversations
    # ---------------------------------------------------------

    def store_conversation(
        self,
        user_id: str,
        message: str,
        response: str,
        emotion: Dict[str, Any],
        timestamp: datetime
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (user_id, message, response, emotion, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, message, response, str(emotion), timestamp.isoformat()))

        self.conn.commit()

    def load_conversation_history(self, user_id: str, limit: int = 1000) -> list[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM conversations
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    # ---------------------------------------------------------
    # Predictions
    # ---------------------------------------------------------

    def save_prediction(self, prediction: Dict[str, Any]) -> None:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (prediction)
            VALUES (json(?))
        """, (prediction,))

        self.conn.commit()

    # ---------------------------------------------------------

    def close(self) -> None:
        self.conn.close()