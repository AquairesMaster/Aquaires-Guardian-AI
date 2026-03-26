 
"""
api.py

This module defines the GuardianAPI, a unified interface layer that sits
between the GuardianHouseAI core and any user-facing interface (CLI, web,
mobile, voice, etc.).

The API:
- Accepts user messages
- Passes them to the orchestrator
- Returns structured Pydantic responses
"""

from __future__ import annotations
from typing import Any, Dict
from .schemas import IntegratedResponse


class GuardianAPI:
    """
    Unified interface for interacting with Guardian House AI.
    """

    def __init__(self, guardian):
        self.guardian = guardian

    async def send_message(self, user_message: str) -> IntegratedResponse:
        """
        Send a message to the Guardian House AI orchestrator.

        Args:
            user_message (str): User input.

        Returns:
            IntegratedResponse: Structured response.
        """
        result = await self.guardian.process_user_input(user_message)
        return IntegratedResponse(**result)

    def generate_forecast(self) -> Dict[str, Any]:
        """
        Generate a multi-domain forecast for the user.

        Returns:
            dict: Forecast results.
        """
        return self.guardian.generate_forecast()



"""
schemas.py

Defines Pydantic models for API responses. These models ensure that all
responses returned to UI layers are structured, validated, and consistent.
"""

from __future__ import annotations
from typing import Dict, List
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """
    Represents a single agent's response.
    """
    agent: str
    content: str


class IntegratedResponse(BaseModel):
    """
    Represents the final synthesized response returned by the API.
    """
    response: str
    intent: str
    emotion: Dict
    agent_responses: Dict[str, str]
    insights: List[str]



"""
cli_adapter.py

A simple command-line interface for interacting with Guardian House AI.
This is useful for local development, debugging, and testing.

Run this adapter from main.py or directly for a REPL-like experience.
"""

from __future__ import annotations
import asyncio


class CLIAdapter:
    """
    Command-line interface adapter for Guardian House AI.
    """

    def __init__(self, api):
        self.api = api

    async def start(self):
        """
        Start the CLI loop.
        """
        print("Guardian House AI CLI — type 'exit' to quit.\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye.")
                break

            response = await self.api.send_message(user_input)
            print(f"\nGuardian: {response.response}\n")



"""
mobile_adapter.py

Stub for a mobile interface adapter. This can later be implemented
using a REST API, WebSocket, or native mobile bridge.
"""


class MobileAdapter:
    """
    Placeholder for mobile UI integration.
    """

    def __init__(self, api):
        self.api = api

    async def send(self, message: str):
        """
        Placeholder method for mobile message handling.
        """
        return await self.api.send_message(message)



"""
web_adapter.py

Stub for a web interface adapter. This can later be implemented using
FastAPI, Flask, or any HTTP framework.
"""


class WebAdapter:
    """
    Placeholder for web UI integration.
    """

    def __init__(self, api):
        self.api = api

    async def handle_request(self, message: str):
        """
        Placeholder method for web request handling.
        """
        return await self.api.send_message(message)



"""
voice_adapter.py

Stub for a voice interface adapter. This can later be integrated with
speech-to-text and text-to-speech systems.
"""


class VoiceAdapter:
    """
    Placeholder for voice UI integration.
    """

    def __init__(self, api):
        self.api = api

    async def process_voice(self, transcript: str):
        """
        Placeholder method for voice input handling.
        """
        return await self.api.send_message(transcript)

