"""
Pydantic schemas for the Architect agent's API contract (endpoints) and
database schema (models + relationships) — the shared source of truth both
frontend and backend workers build against.

Run: not run directly — imported by architect.py, frontend.py, backend.py,
     state.py.

Learn: Field(default_factory=dict/list) for optional nested structures, and
how one schema (APIContract) is deliberately shared by two different
workers.
"""

from pydantic import BaseModel, Field


class APIEndpoint(BaseModel):
    method: str
    path: str
    description: str

    request_schema: dict = Field(default_factory=dict)
    response_schema: dict = Field(default_factory=dict)


class APIContract(BaseModel):
    """Shared contract consumed by FE and BE workers."""

    endpoints: list[APIEndpoint]


class DatabaseModel(BaseModel):
    name: str
    fields: dict[str, str]
    relationships: list[str] = Field(default_factory=list)


class SchemaSpec(BaseModel):
    """Database schema specification."""

    models: list[DatabaseModel]