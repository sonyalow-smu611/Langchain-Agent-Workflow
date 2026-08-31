"""
Pydantic schema for the Director agent's first structured output: what the
user wants built.

Run: not run directly — a data model imported wherever a ProductSpec is
     produced (director.py) or consumed (architect.py, state.py).

Learn: pydantic.Field(description=...) — descriptions become part of the
JSON schema the LLM sees when using .with_structured_output(ProductSpec).
"""

from pydantic import BaseModel, Field


class ProductSpec(BaseModel):
    """Structured description of what the user wants to build."""

    goal: str = Field(
        description="The primary goal of the application."
    )

    target_users: list[str] = Field(
        description="Users who will use the application."
    )

    mvp_features: list[str] = Field(
        description="Features that must be included in the MVP."
    )

    out_of_scope: list[str] = Field(
        default_factory=list,
        description="Features intentionally excluded from the MVP."
    )

    acceptance_criteria: list[str] = Field(
        description="Conditions that determine whether the product is complete."
    )