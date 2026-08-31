"""
Pydantic schema for the Architect agent's technical blueprint: project
structure, key decisions + rationale, and FE/BE requirements.

Run: not run directly — imported by architect.py and state.py.

Learn: nesting one Pydantic model inside another (ArchitectureDecision
inside BlueprintSpec) to get structured sub-objects, not just flat fields.
"""

from pydantic import BaseModel, Field


class ArchitectureDecision(BaseModel):
    technology: str
    decision: str
    rationale: str


class BlueprintSpec(BaseModel):
    """Technical blueprint produced by the Architect."""

    project_structure: list[str]

    architecture_summary: str

    decisions: list[ArchitectureDecision]

    frontend_requirements: list[str]

    backend_requirements: list[str]