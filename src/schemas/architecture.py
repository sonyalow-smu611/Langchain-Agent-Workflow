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