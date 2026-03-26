 
"""
guardian.py

This module defines the GuardianHouseAI class, the central orchestrator
of the entire Guardian House system. It coordinates:

- Intent classification
- Emotional analysis
- Context + memory management
- Multi-agent routing
- Cross-domain synthesis
- Predictive modeling
- Database persistence

This is the "brain" of the system.
"""

from __future__ import annotations
from typing import Dict, Any
from datetime import datetime

from .user_model import UserLifeModel
from .database import Database
from .context_manager import ContextManager
from .intent_classifier import IntentClassifier
from .emotional_engine import EmotionalEngine
from .synthesis_engine import SynthesisEngine
from .predictive_engine import PredictiveEngine


class GuardianHouseAI:
    """
    Central orchestrator for the Guardian House AI system.

    This class provides the main entry point for all user interactions.
    """

    def __init__(
        self,
        user_id: str,
        db: Database,
        context: ContextManager,
        intent_classifier: IntentClassifier,
        emotional_engine: EmotionalEngine,
        synthesis_engine: SynthesisEngine,
        predictive_engine: PredictiveEngine,
        agents: Dict[str, Any],
    ):
        self.user_id = user_id
        self.db = db
        self.context = context
        self.intent_classifier = intent_classifier
        self.emotional_engine = emotional_engine
        self.synthesis_engine = synthesis_engine
        self.predictive_engine = predictive_engine
        self.agents = agents

        # Load or create user model
        model = self.db.load_user_model(user_id)
        if model is None:
            model = UserLifeModel(
                user_id=user_id,
                birth_date=datetime.utcnow(),
                current_stage="young_adult",
            )
            self.db.save_user_model(model)

        self.user_model = model

    # ------------------------------------------------------------------
    # Main Interaction Loop
    # ------------------------------------------------------------------

    async def process_user_input(self, message: str) -> Dict[str, Any]:
        """
        Main entry point for all user interactions.

        Args:
            message (str): User message.

        Returns:
            dict: Structured response for the API layer.
        """

        # 1. Classify intent
        intent = self.intent_classifier.classify(message)

        # 2. Analyze emotional tone
        emotion = self.emotional_engine.analyze(message)

        # 3. Update context + memory
        self.context.update_history(message, emotion)

        # 4. Route to agents
        agent_responses = await self.context.router.route(message, intent)

        # 5. Synthesize final response
        integrated = self.synthesis_engine.combine(
            message=message,
            intent=intent,
            emotion=emotion,
            agent_responses=agent_responses,
            user_model=self.user_model
        )

        # 6. Persist conversation
        self.db.store_conversation(
            user_id=self.user_id,
            message=message,
            response=integrated["response"],
            emotion=emotion,
            timestamp=datetime.utcnow()
        )

        return integrated

    # ------------------------------------------------------------------
    # Forecasting API
    # ------------------------------------------------------------------

    def generate_forecast(self) -> Dict[str, Any]:
        """
        Generate a multi-domain forecast for the user.

        Returns:
            dict: Forecast results.
        """
        return self.predictive_engine.generate_forecast(self.user_model)

