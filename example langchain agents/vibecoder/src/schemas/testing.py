"""
Pydantic schemas for the QA/repair loop: TestReport (pass/fail + failures)
and RepairTicket (one bug to fix).

Run: not run directly — TestReport is produced by tools/testing.py's
     run_tests() and consumed by agents/qa_repair.py's run_qa().

Learn: `str | None` for an optional field, and how a plain Python subprocess
result (pytest output) becomes a typed Pydantic object other agents can
reason about.
"""

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