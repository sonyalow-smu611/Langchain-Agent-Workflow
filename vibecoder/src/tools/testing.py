"""
Runs the project's pytest suite as a subprocess and turns the result into a
structured TestReport for the QA agent to reason about.

Run: not run directly — call `run_tests()` yourself to see the TestReport it
     builds, or trace how agents/qa_repair.py's run_qa() consumes it.

Learn: turning an external command's exit code + stdout/stderr into a typed
Pydantic result — notice it reports one generic failure rather than parsing
pytest's real per-test output, a good gap to fix as a self-study exercise.
"""

import subprocess

from vibecoder.src.schemas.testing import TestReport, TestFailure


def run_tests() -> TestReport:
    """
    Run the project's tests and return a structured report.
    """

    result = subprocess.run(
        ["pytest"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return TestReport(
            status="passed",
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            failures=[]
        )

    return TestReport(
        status="failed",
        tests_run=0,
        tests_passed=0,
        tests_failed=1,
        failures=[
            TestFailure(
                test_name="pytest",
                error=result.stdout + result.stderr
            )
        ]
    )