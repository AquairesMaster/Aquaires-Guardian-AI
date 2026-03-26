"""
user_model.py

This module defines the core Pydantic data models used by Guardian House AI.
It includes the UserLifeModel, which represents the long-term evolving profile
of the user, as well as enumerations for life stages and relationship modes.

These models are central to the system because they:
- Provide validated, structured data for all subsystems
- Allow clean JSON serialization for SQLite/PostgreSQL storage
- Enable predictable behavior across agents and orchestration layers
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class LifeStage(str, Enum):
    """
    Enumeration representing the major stages of human development.
    Guardian House AI uses this to adjust tone, autonomy, privacy,
    and the type of guidance it provides.
    """
    infant = "infant"            # 0–2
    child = "child"              # 3–12
    adolescent = "adolescent"    # 13–19
    young_adult = "young_adult"  # 20–35
    adult = "adult"              # 36–55
    mature = "mature"            # 56–75
    elder = "elder"              # 75+


class RelationshipMode(str, Enum):
    """
    Defines the relational stance Guardian House AI takes toward the user.
    This evolves over time based on trust, age, emotional history, and context.
    """
    caregiver = "caregiver"
    teacher = "teacher"
    mentor = "mentor"
    friend = "friend"
    partner = "partner"


class UserLifeModel(BaseModel):
    """
    The central long-term model of the user's identity, history, and life domains.

    This model is:
    - Persisted in the database (SQLite or PostgreSQL)
    - Loaded at startup and updated continuously
    - Used by all subsystems (agents, predictive engine, synthesis engine)
    - Serialized/deserialized using Pydantic for safety and consistency
    """

    # Core identity
    user_id: str
    birth_date: datetime
    current_stage: LifeStage

    values: List[str] = Field(default_factory=list, description="User's core values")
    fears: List[str] = Field(default_factory=list, description="User's fears or anxieties")
    aspirations: List[str] = Field(default_factory=list, description="Long-term goals and dreams")
    strengths: List[str] = Field(default_factory=list, description="User's strengths")
    growth_areas: List[str] = Field(default_factory=list, description="Areas for improvement")

    # Relationship with Guardian House AI
    relationship_mode: RelationshipMode = RelationshipMode.caregiver
    trust_level: float = Field(default=0.5, ge=0.0, le=1.0)
    interaction_history: List[Dict] = Field(default_factory=list)

    # Life domains (updated by specialized agents)
    health_status: Dict = Field(default_factory=dict)
    financial_status: Dict = Field(default_factory=dict)
    security_status: Dict = Field(default_factory=dict)
    learning_status: Dict = Field(default_factory=dict)
    physical_status: Dict = Field(default_factory=dict)
    social_status: Dict = Field(default_factory=dict)

    # Predictive modeling fields
    behavioral_patterns: Dict = Field(default_factory=dict)
    risk_factors: Dict = Field(default_factory=dict)
    opportunity_windows: List[Dict] = Field(default_factory=list)

    class Config:
        """
        Pydantic configuration for serialization and forward compatibility.
        """
        validate_assignment = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
        