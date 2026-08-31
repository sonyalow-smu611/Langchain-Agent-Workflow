"""
Pydantic schema for the Director agent's task graph — the list of Task
objects (with owner, dependencies) that later stages would execute.

Run: not run directly — imported by director.py and state.py.

Learn: typing.Literal to constrain a field to a fixed set of values (here,
which team owns a task), so the LLM can only pick a valid owner.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Task(BaseModel):
    id: str

    owner: Literal[
        "frontend",
        "backend",
        "qa"
    ]

    description: str

    files: list[str] = Field(default_factory=list)

    dependencies: list[str] = Field(default_factory=list)


class TaskGraph(BaseModel):
    tasks: list[Task]