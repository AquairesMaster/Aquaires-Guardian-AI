 
"""
router.py

This module defines the AgentRouter, responsible for selecting and invoking
the appropriate specialized agents based on the user's intent.

The router:
- Maps intents to agent subsets
- Executes agents asynchronously
- Returns a dictionary of agent responses
- Supports cross-domain queries by invoking all agents

This is the "traffic controller" of the multi-agent system.
"""

from __future__ import annotations
from typing import Dict, Any


class AgentRouter:
    """
    Routes user messages to the appropriate specialized agents.

    Attributes:
        agents (dict[str, BaseAgent]): Mapping of agent names to agent instances.
    """

    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents

        # Intent → agent mapping
        self.intent_map = {
            "finance": ["bookie"],
            "health": ["doctor"],
            "security": ["berserker"],
            "learning": ["teacher"],
            "physical": ["sensei"],
            "supplies": ["broker"],
            "cross_domain": list(agents.keys()),
        }

    # ------------------------------------------------------------------
    # Agent Selection
    # ------------------------------------------------------------------

    def _select_agents(self, intent: str) -> Dict[str, Any]:
        """
        Select agents based on the user's intent.

        Args:
            intent (str): Classified intent.

        Returns:
            dict[str, BaseAgent]: Selected agents.
        """
        agent_names = self.intent_map.get(intent, [])

        # If no direct mapping, default to general conversation agents
        if not agent_names:
            agent_names = ["sensei", "teacher"]  # fallback conversational agents

        return {name: self.agents[name] for name in agent_names if name in self.agents}

    # ------------------------------------------------------------------
    # Routing Execution
    # ------------------------------------------------------------------

    async def route(self, message: str, intent: str) -> Dict[str, str]:
        """
        Invoke selected agents asynchronously and collect responses.

        Args:
            message (str): User message.
            intent (str): Classified intent.

        Returns:
            dict[str, str]: Agent name → response text.
        """
        selected = self._select_agents(intent)
        responses = {}

        for name, agent in selected.items():
            try:
                responses[name] = await agent.respond(message)
            except Exception as e:
                responses[name] = f"[Error from {name}: {e}]"

        return responses
