 
"""
predictive_engine.py

This module defines the PredictiveEngine, responsible for generating
forecasts, risk assessments, and opportunity windows based on the user's
historical data, behavioral patterns, and domain statuses.

This is a simplified, production-stable version that can later be
extended with ML models (e.g., Gradient Boosting, Isolation Forest,
time-series forecasting, etc.).

The predictive engine supports:
- Health trajectory forecasting
- Financial trajectory forecasting
- Social/relationship trajectory forecasting
- Achievement/progress forecasting
- Risk factor detection
- Opportunity window detection
"""

from __future__ import annotations
from typing import Dict, Any
from datetime import datetime


class PredictiveEngine:
    """
    Lightweight predictive modeling engine.

    This engine uses rule-based heuristics for stability and clarity.
    It can be replaced with ML models later without changing the interface.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Health Forecast
    # ------------------------------------------------------------------

    def _predict_health(self, user_model) -> Dict[str, Any]:
        """
        Predict future health trajectory based on current risk factors.

        Args:
            user_model (UserLifeModel): The user's profile.

        Returns:
            dict: Health forecast.
        """

        health = user_model.health_status
        stress = health.get("stress_level", 0)
        sleep = health.get("sleep_quality", 80)
        fitness = health.get("fitness_score", 70)

        projected = max(0, min(100, fitness - stress * 0.3 + (sleep - 70) * 0.2))

        return {
            "projected_health_score": projected,
            "risk_factors": health.get("risk_factors", []),
            "recommendations": [
                "Improve sleep consistency",
                "Reduce stress through mindfulness or exercise",
                "Increase moderate physical activity"
            ]
        }

    # ------------------------------------------------------------------
    # Financial Forecast
    # ------------------------------------------------------------------

    def _predict_finances(self, user_model) -> Dict[str, Any]:
        """
        Predict financial trajectory using simple compound growth modeling.

        Args:
            user_model (UserLifeModel): The user's profile.

        Returns:
            dict: Financial forecast.
        """

        finance = user_model.financial_status
        net_worth = finance.get("net_worth", 0)
        savings_rate = finance.get("savings_rate", 0.1)
        income = finance.get("income", 50000)
        avg_return = finance.get("avg_return", 0.07)

        projected = net_worth * (1 + avg_return) + income * savings_rate

        return {
            "projected_net_worth_next_year": projected,
            "recommendations": [
                "Increase savings rate if possible",
                "Diversify investments",
                "Review spending habits monthly"
            ]
        }

    # ------------------------------------------------------------------
    # Social Forecast
    # ------------------------------------------------------------------

    def _predict_social(self, user_model) -> Dict[str, Any]:
        """
        Predict social/relationship trajectory.

        Args:
            user_model (UserLifeModel): The user's profile.

        Returns:
            dict: Social forecast.
        """

        social = user_model.social_status
        connections = social.get("connection_score", 50)
        activity = social.get("social_activity", 3)

        projected = min(100, connections + activity * 2)

        return {
            "projected_connection_score": projected,
            "recommendations": [
                "Reach out to close friends weekly",
                "Engage in group activities",
                "Strengthen meaningful relationships"
            ]
        }

    # ------------------------------------------------------------------
    # Achievement Forecast
    # ------------------------------------------------------------------

    def _predict_achievement(self, user_model) -> Dict[str, Any]:
        """
        Predict progress in learning, career, or personal goals.

        Args:
            user_model (UserLifeModel): The user's profile.

        Returns:
            dict: Achievement forecast.
        """

        learning = user_model.learning_status
        progress = learning.get("progress_score", 60)

        projected = min(100, progress + 5)

        return {
            "projected_progress_score": projected,
            "recommendations": [
                "Set weekly learning goals",
                "Use spaced repetition",
                "Track progress monthly"
            ]
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_forecast(self, user_model) -> Dict[str, Any]:
        """
        Generate a full multi-domain forecast.

        Args:
            user_model (UserLifeModel): The user's profile.

        Returns:
            dict: Multi-domain forecast.
        """

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health": self._predict_health(user_model),
            "finances": self._predict_finances(user_model),
            "social": self._predict_social(user_model),
            "achievement": self._predict_achievement(user_model),
        }
