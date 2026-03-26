 
"""
db_postgres.py

PostgreSQL implementation of the Database interface.

This backend is ideal for:
- Cloud deployments
- Multi-user systems
- High concurrency environments
- Scalable production systems

Uses JSONB for Pydantic model storage.
"""

import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Dict, Any
from pydantic import ValidationError
from .database import Database
from .user_model import UserLifeModel


class PostgresDatabase(Database):
    """
    PostgreSQL implementation of the Guardian House database layer.
    """

    def __init__(self, dsn: str):
        self.conn = psycopg2.connect(dsn)
        self._init_tables()

    def _init_tables(self) -> None:
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_model (
                user_id TEXT PRIMARY KEY,
                data JSONB NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                message TEXT,
                response TEXT,
                emotion JSONB,
                timestamp TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                prediction JSONB
            )
        """)

        self.conn.commit()

    # ---------------------------------------------------------
    # User Model
    # ---------------------------------------------------------

    def load_user_model(self, user_id: str) -> UserLifeModel | None:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT data FROM user_model WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()

        if not row:
            return None

        try:
            return UserLifeModel.model_validate(row["data"])
        except ValidationError:
            return None

    def save_user_model(self, model: UserLifeModel) -> None:
        cursor = self.conn.cursor()
        json_data = model.model_dump()

        cursor.execute("""
            INSERT INTO user_model (user_id, data)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE SET data = EXCLUDED.data
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
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, message, response, emotion, timestamp))

        self.conn.commit()

    def load_conversation_history(self, user_id: str, limit: int = 1000) -> list[Dict]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT * FROM conversations
            WHERE user_id=%s
            ORDER BY id DESC
            LIMIT %s
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
            VALUES (%s)
        """, (prediction,))

        self.conn.commit()

    # ---------------------------------------------------------

    def close(self) -> None:
        self.conn.close()
