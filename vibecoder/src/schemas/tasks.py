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