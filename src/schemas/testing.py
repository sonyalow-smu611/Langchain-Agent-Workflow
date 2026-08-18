from typing import Literal

from pydantic import BaseModel, Field


class TestFailure(BaseModel):
    test_name: str
    error: str
    file: str | None = None


class TestReport(BaseModel):
    status: Literal["passed", "failed"]

    tests_run: int

    tests_passed: int

    tests_failed: int

    failures: list[TestFailure] = Field(default_factory=list)


class RepairTicket(BaseModel):
    issue_id: str

    description: str

    file: str | None = None

    error: str

    expected_behavior: str

    suggested_owner: Literal[
        "frontend",
        "backend"
    ]

    attempt: int = 1