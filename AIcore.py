 
"""
main.py

Entry point for the Guardian House AI system.

This script:
- Configures logging
- Loads the database backend (SQLite by default)
- Instantiates all agents
- Builds the router and context manager
- Creates the GuardianHouseAI orchestrator
- Wraps it in the GuardianAPI
- Starts the CLI interface

Run this file to launch the system.
"""

import asyncio
import logging

from utils.logging_config import configure_logging
from core.db_sqlite import SQLiteDatabase
from core.router import AgentRouter
from core.context_manager import ContextManager
from core.intent_classifier import IntentClassifier
from core.emotional_engine import EmotionalEngine
from core.synthesis_engine import SynthesisEngine
from core.predictive_engine import PredictiveEngine
from core.guardian import GuardianHouseAI

from agents.bookie import BookieAgent
from agents.doctor import DoctorAgent
from agents.berserker import BerserkerAgent
from agents.sensei import SenseiAgent
from agents.teacher import TeacherAgent
from agents.broker import BrokerAgent

from interface.api import GuardianAPI
from interface.adapters.cli_adapter import CLIAdapter


async def main():
    """
    Initialize and run the Guardian House AI system.
    """

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------
    configure_logging(logging.INFO)

    # ---------------------------------------------------------
    # Database Backend
    # ---------------------------------------------------------
    db = SQLiteDatabase("guardian_house.db")

    # ---------------------------------------------------------
    # Agents
    # ---------------------------------------------------------
    agents = {
        "bookie": BookieAgent(),
        "doctor": DoctorAgent(),
        "berserker": BerserkerAgent(),
        "sensei": SenseiAgent(),
        "teacher": TeacherAgent(),
        "broker": BrokerAgent(),
    }

    # ---------------------------------------------------------
    # Router + Context
    # ---------------------------------------------------------
    router = AgentRouter(agents)
    context = ContextManager(router=router, db=db)

    # ---------------------------------------------------------
    # Core Engines
    # ---------------------------------------------------------
    intent_classifier = IntentClassifier()
    emotional_engine = EmotionalEngine()
    synthesis_engine = SynthesisEngine()
    predictive_engine = PredictiveEngine()

    # ---------------------------------------------------------
    # Orchestrator
    # ---------------------------------------------------------
    guardian = GuardianHouseAI(
        user_id="default_user",
        db=db,
        context=context,
        intent_classifier=intent_classifier,
        emotional_engine=emotional_engine,
        synthesis_engine=synthesis_engine,
        predictive_engine=predictive_engine,
        agents=agents,
    )

    # ---------------------------------------------------------
    # API Layer
    # ---------------------------------------------------------
    api = GuardianAPI(guardian)

    # ---------------------------------------------------------
    # CLI Interface
    # ---------------------------------------------------------
    cli = CLIAdapter(api)
    await cli.start()


if __name__ == "__main__":
    asyncio.run(main())

