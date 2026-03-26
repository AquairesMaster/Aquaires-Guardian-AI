 """
base_agent.py

Defines the BaseAgent class, which all specialized agents inherit from.
This provides a consistent async interface and shared utilities.

Agents are intentionally lightweight wrappers around LLM calls or
domain-specific logic. They can be replaced or extended without
changing the rest of the system.
"""

from __future__ import annotations
from typing import Any


class BaseAgent:
    """
    Base class for all Guardian House AI agents.

    Each agent must implement:
        async def respond(self, message: str) -> str
    """

    name: str = "base"

    async def respond(self, message: str) -> str:
        """
        Default implementation. Should be overridden.

        Args:
            message (str): User message.

        Returns:
            str: Agent response.
        """
        return f"[{self.name}] No implementation provided."



"""
bookie.py

Finance agent responsible for:
- Budgeting
- Spending analysis
- Investment basics
- Savings recommendations
"""

from __future__ import annotations
from .base_agent import BaseAgent


class BookieAgent(BaseAgent):
    name = "bookie"

    async def respond(self, message: str) -> str:
        return (
            "From a financial perspective, here's what I suggest: "
            "review your spending categories, increase savings rate if possible, "
            "and consider low-risk diversified investments."
        )



"""
doctor.py

Health agent responsible for:
- Sleep
- Diet
- Stress
- Exercise
- General wellness
"""

from __future__ import annotations
from .base_agent import BaseAgent


class DoctorAgent(BaseAgent):
    name = "doctor"

    async def respond(self, message: str) -> str:
        return (
            "From a health standpoint, focus on consistent sleep, "
            "balanced nutrition, hydration, and moderate daily movement."
        )



"""
berserker.py

Security agent responsible for:
- Personal safety
- Risk awareness
- Threat assessment
- Digital security basics
"""

from __future__ import annotations
from .base_agent import BaseAgent


class BerserkerAgent(BaseAgent):
    name = "berserker"

    async def respond(self, message: str) -> str:
        return (
            "From a security perspective, stay aware of your surroundings, "
            "trust your instincts, and ensure your digital accounts use strong authentication."
        )



"""
sensei.py

Physical training agent responsible for:
- Exercise
- Strength
- Mobility
- Discipline
"""

from __future__ import annotations
from .base_agent import BaseAgent


class SenseiAgent(BaseAgent):
    name = "sensei"

    async def respond(self, message: str) -> str:
        return (
            "Physically, aim for steady progress: consistent workouts, "
            "proper form, and recovery through stretching and hydration."
        )



"""
teacher.py

Learning agent responsible for:
- Study habits
- Skill acquisition
- Memory techniques
- Productivity
"""

from __future__ import annotations
from .base_agent import BaseAgent


class TeacherAgent(BaseAgent):
    name = "teacher"

    async def respond(self, message: str) -> str:
        return (
            "For learning, break tasks into small chunks, use spaced repetition, "
            "and review material actively rather than passively."
        )


"""
broker.py

Supplies/logistics agent responsible for:
- Inventory
- Restocking
- Planning
- Resource management
"""

from __future__ import annotations
from .base_agent import BaseAgent


class BrokerAgent(BaseAgent):
    name = "broker"

    async def respond(self, message: str) -> str:
        return (
            "From a supplies standpoint, keep essential items stocked, "
            "track usage patterns, and plan ahead for replenishment."
        )







